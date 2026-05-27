from typing import Optional, Literal, Union, Dict, Any
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
import time
import gc
import os
import sys
import ccxt
from sqlalchemy import create_engine
from sklearn.metrics import accuracy_score
import catboost as cb
from dataBaseModels import Session, Signal
from logger_setup import get_logger

logger = get_logger(__name__)

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)

def main(inputMessage: Dict[str, Any]) -> None:

	nowMuchMoreDays = 365
	windowFeatures0 = 5
	windowFeatures1 = 10
	windowFeatures2 = 15
	centreMoving = 20
	quantile = 0.90

	if inputMessage['timeFrame'] == "15min":
		amountDays = 22
	elif inputMessage['timeFrame'] == "30min":
		amountDays = 44
	elif inputMessage['timeFrame'] == "1h":
		amountDays = 88
	elif inputMessage['timeFrame'] == "2h":
		amountDays = 176
	elif inputMessage['timeFrame'] == "4h":
		amountDays = 352

	dataFrame = dataFrameDownloader(
		symbol=inputMessage['symbol'],
		nameExchange='binance',
		amountDays=amountDays,
		timeFrame=inputMessage['timeFrame'],
		nowMuchMoreDays=nowMuchMoreDays
	)

	dataFrame['features0'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures0))/dataFrame['close'].shift(windowFeatures0)
	dataFrame['features1'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures1))/dataFrame['close'].shift(windowFeatures1)
	dataFrame['features2'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures2))/dataFrame['close'].shift(windowFeatures2)

	dataFrame['centreMoving'] = dataFrame['close'].rolling(window=centreMoving).mean().shift(-centreMoving//2)
	diff = dataFrame['centreMoving'].diff()
	dataFrame['classEDU'] = (diff < 0).astype(int)

	workDataFrame = dataFrame.iloc[windowFeatures2:]

	uniCut = int(len(workDataFrame)*quantile)

	yTrain = np.array(workDataFrame['classEDU'])[:uniCut]
	xTrain = workDataFrame[['features0', 'features1', 'features2']].iloc[:uniCut].to_numpy()

	yTest = np.array(workDataFrame['classEDU'])[uniCut:]
	xTest = workDataFrame[['features0', 'features1', 'features2']].iloc[uniCut:].to_numpy()

	model = cb.CatBoostClassifier(
		iterations=50,
		learning_rate=0.1,
		depth=4,
		loss_function='Logloss',
		random_seed=42,
		verbose=False
	)

	model.fit(xTrain, yTrain)

	yPredict = model.predict(xTrain)
	accuracy = accuracy_score(yTrain, yPredict)
	logger.info(f"Точность модели на Train: {100*accuracy:.2f} %")

	importance = model.feature_importances_
	for i in range(len(importance)):
		logger.info(f"Важность фичи номер {i}: > {importance[i]:.2f} % <")

	yPredict = model.predict(xTest)
	accuracy = accuracy_score(yTest, yPredict)
	logger.info(f"Точность модели на Test: {100*accuracy:.2f} %")

	if yPredict[-1] == 0:
		tradingSignal = "long"
	elif yPredict[-1] == 1:
		tradingSignal = "short"
	else:
		tradingSignal = "neutral"
	
	logger.info(f"tradingSignal = {tradingSignal}")

	dataBaseSession = Session()

	try:
		dataBaseSession.query(Signal).filter(
			Signal.asset == inputMessage['symbol'],
			Signal.timeframe == inputMessage['timeFrame']
		).delete()
		
		newSignal = Signal(
			asset=inputMessage['symbol'],
			ml_model="CatBoostClass",
			timeframe=inputMessage['timeFrame'],
			signal=tradingSignal,
			accuracy=f"{100*accuracy:.2f} %",
		)
		dataBaseSession.add(newSignal)
		dataBaseSession.commit()
		
		logger.info(f"Saved {inputMessage['symbol']} {inputMessage['timeFrame']} -> {tradingSignal} with id={newSignal.id}")
		
	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
	
	finally:
		dataBaseSession.close()

def dataFrameDownloader(
		symbol: str,
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		amountDays: int,
		timeFrame: Literal['15min', '30min', '1h', '2h', '4h'],
		nowMuchMoreDays: int = 365
	) -> pd.DataFrame:
	
	oneDay = 1440
	maxDelta = 15
	realAmountLines = oneDay*amountDays
	nameTable = f"{nameExchange}_{symbol}".lower()

	queryCode = f"""
		SELECT * FROM (
			SELECT * FROM {nameTable}
			ORDER BY datetime DESC
			LIMIT {realAmountLines}
		) AS last_rows
		ORDER BY datetime ASC
	"""

	try:
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} is exist! Fetched last {realAmountLines} rows')
		pastDatetime = dataFrame['datetime'].iloc[-1]
		nowDatetime = datetime.utcnow()
		maxDeltaDatetime = timedelta(minutes=maxDelta)

		if (nowDatetime - pastDatetime) > maxDeltaDatetime:
			logger.info(f'{nameTable} is very old! Downloading fresh data...')

			del dataFrame
			gc.collect()

			downloadHistory(symbol, nameExchange, nowMuchMoreDays)

			dataFrame = pd.read_sql(queryCode, engine)
			logger.info(f'{nameTable} fetched last {realAmountLines} rows')
	
	except Exception as error_body:
		logger.info(f'{nameTable} does NOT exist. Downloading...')
		downloadHistory(symbol, nameExchange, nowMuchMoreDays)
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} fetched last {realAmountLines} rows')

	logger.info(f"\n>>>>>\n {dataFrame.tail(5)} \n>>>>>\n")

	dataFrame.set_index('datetime', inplace=True)
	dataFrame = dataFrame.resample(timeFrame).agg({
		'open': 'first',
		'high': 'max',
		'low': 'min',
		'close': 'last',
		'volume': 'sum'
	})
	dataFrame.reset_index(inplace=True)

	logger.info(f"\n>>>>>\n {dataFrame.tail(5)} \n>>>>>\n")

	return dataFrame

def downloadHistory(
		symbol: str,
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		nowMuchMoreDays: int = 365
	) -> None:

	if nameExchange == 'binance':
		exchange = ccxt.binance()
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()

	nameTable = f"{nameExchange}_{symbol}".lower()
	ticker = f'{symbol}/USDT'
	timeFrame = '1m'
	timeFramePandas = '1min'
	deltaDatetime = timedelta(minutes=1)
	limit = 1000
	initialDatetime = datetime.utcnow() - timedelta(days=nowMuchMoreDays)
	newDataFrame = True

	logger.info(nameTable)
	logger.info(f'Start parsing new data! From initialDatetime => {initialDatetime}')

	while True:
		iso_string = initialDatetime.strftime('%Y-%m-%dT%H:%M:%SZ')
		since = exchange.parse8601(iso_string)
		ohlcv = exchange.fetch_ohlcv(ticker, timeFrame, since, limit)

		dataFrame = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
		dataFrame['datetime'] = dataFrame['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x / 1000))
		dataFrame = dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume']]
		initialDatetime = dataFrame['datetime'][len(dataFrame)-1]
		if newDataFrame:
			zeroDataFrame = dataFrame.copy()
			newDataFrame = False
		else:
			zeroDataFrame = pd.concat([zeroDataFrame, dataFrame], ignore_index=True)

		nowDatetime = datetime.utcnow()
		logger.info(f"{nameTable} <=> {initialDatetime}")
		if initialDatetime > (nowDatetime - deltaDatetime):
			break

	zeroDataFrame['datetime'] = pd.to_datetime(zeroDataFrame['datetime'])
	zeroDataFrame.set_index('datetime', inplace=True)
	zeroDataFrame = zeroDataFrame[~zeroDataFrame.index.duplicated(keep='first')]
	
	min_date = zeroDataFrame.index.min()
	max_date = zeroDataFrame.index.max()
	fullIndexes = pd.date_range(start=min_date, end=max_date, freq=timeFramePandas)
	zeroDataFrame = zeroDataFrame.reindex(fullIndexes).ffill()
	
	zeroDataFrame.reset_index(inplace=True, names=['datetime'])

	del fullIndexes
	gc.collect()

	logger.info(f'Start save {nameTable} in dataBase!')
	zeroDataFrame.to_sql(nameTable, con=engine, if_exists='replace', chunksize=5000, method='multi')
	logger.info(f'{nameTable} is saved to dataBase!')

	del zeroDataFrame
	gc.collect()

main({'symbol': 'BTC', 'timeFrame': '15min'})