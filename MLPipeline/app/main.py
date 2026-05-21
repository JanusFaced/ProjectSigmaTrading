from datetime import datetime, timedelta, timezone
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import os
import sys
import logging
import make_logger
import ccxt
from sqlalchemy import create_engine
from sklearn.metrics import accuracy_score
import catboost as cb

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('MLPipeline:main')

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)

def main():

	inputMessage = {
		"symbol": "BTC",
		"timeFrame" "1d"
	}

	dataFrame = dataFrameDownloader(
		symbol=inputMessage['symbol'],
		nameExchange='binance',
		amountDays=6*365,
		timeFrame=inputMessage['timeFrame']
	)

	windowFeatures0 = 5
	windowFeatures1 = 10
	windowFeatures2 = 15

	centreMoving = 20
	quantile = 0.90

	dataFrame['features0'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures0))/dataFrame['close'].shift(windowFeatures0)
	dataFrame['features1'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures1))/dataFrame['close'].shift(windowFeatures1)
	dataFrame['features2'] = (dataFrame['close'] - dataFrame['close'].shift(windowFeatures2))/dataFrame['close'].shift(windowFeatures2)

	dataFrame['centreMoving'] = dataFrame['close'].rolling(window=centreMoving).mean().shift(-int(centreMoving/2))
	dataFrame['diffCentreMoving'] = dataFrame['centreMoving'] - dataFrame['centreMoving'].shift(1)

	dataFrame['classEDU'] = np.select(
			[
				(dataFrame['diffCentreMoving'] > 0),
				(dataFrame['diffCentreMoving'] < 0)
			],
			[0, 1],
			default=0
		)

	plt.plot(dataFrame['datetime'], dataFrame['close'])
	plt.plot(dataFrame['datetime'], dataFrame['close']*(1+(dataFrame['classEDU'] - 0.5)/20))
	plt.savefig(str(current_dir/'output'/'plot0.png'))
	plt.close()

	workDataFrame = dataFrame.iloc[windowFeatures2:]

	uniCut = int(len(workDataFrame)*quantile)

	datetimeTrain = workDataFrame['datetime'][:uniCut]
	closeTrain = workDataFrame['close'][:uniCut]
	yTrain = np.array(workDataFrame['classEDU'])[:uniCut]
	vectorF0 = np.array(workDataFrame['features0']).reshape(-1, 1)[:uniCut]
	vectorF1 = np.array(workDataFrame['features1']).reshape(-1, 1)[:uniCut]
	vectorF2 = np.array(workDataFrame['features2']).reshape(-1, 1)[:uniCut]
	xTrain = np.column_stack((vectorF0, vectorF1, vectorF2))

	datetimeTest = workDataFrame['datetime'][uniCut:]
	closeTest = workDataFrame['close'][uniCut:]
	yTest = np.array(workDataFrame['classEDU'])[uniCut:]
	vectorF0 = np.array(workDataFrame['features0']).reshape(-1, 1)[uniCut:]
	vectorF1 = np.array(workDataFrame['features1']).reshape(-1, 1)[uniCut:]
	vectorF2 = np.array(workDataFrame['features2']).reshape(-1, 1)[uniCut:]
	xTest = np.column_stack((vectorF0, vectorF1, vectorF2))

	model = cb.CatBoostClassifier(
		iterations=100,
		learning_rate=0.1,
		depth=5,
		loss_function='Logloss',
		random_seed=42,
		verbose=False
	)

	model.fit(xTrain, yTrain)

	yPredict = model.predict(xTrain)
	accuracy = accuracy_score(yTrain, yPredict)
	logger.info(f"Точность модели: {100*accuracy:.2f} %")

	importance = model.feature_importances_
	for i in range(len(importance)):
		logger.info(f"{i}: {importance[i]:.3f}")

	plt.plot(datetimeTrain, closeTrain)
	plt.plot(datetimeTrain, closeTrain*(1+(yPredict - 0.5)/20))
	plt.savefig(str(current_dir/'output'/'plot1.png'))
	plt.close()

	yPredict = model.predict(xTest)
	plt.plot(datetimeTest, closeTest)
	plt.plot(datetimeTest, closeTest*(1+(yPredict - 0.5)/20))
	plt.savefig(str(current_dir/'output'/'plot2.png'))
	plt.close()

	logger.info('End!')

def dataFrameDownloader(symbol, nameExchange, amountDays, timeFrame):
	nameTable = f"{nameExchange}_{symbol}".lower()

	try:
		dataFrame = pd.read_sql(f"SELECT * FROM {nameTable}", engine)
		logger.info(f'{nameTable} is exist!')
	
	except Exception as error_body:
		logger.info(f'{nameTable} is NO exist...')
		downloadHistory(symbol, nameExchange)
		dataFrame = pd.read_sql(f"SELECT * FROM {nameTable}", engine)

	oneDay = 1440
	dataFrame = dataFrame.tail(oneDay*amountDays)

	dataFrame = dataFrame.set_index('datetime')
	dataFrame = dataFrame.resample(timeFrame).agg({
		'open': 'first',
		'high': 'max',
		'low': 'min',
		'close': 'last',
		'volume': 'sum'
	})
	dataFrame = dataFrame.reset_index()

	return dataFrame

def downloadHistory(symbol, nameExchange):
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
	newDataFrame = False
	logger.info(nameTable)
	
	try:
		zeroDataFrame = pd.read_sql(nameTable, engine)
		zeroDataFrame['datetime'] = pd.to_datetime(zeroDataFrame['datetime'])
		zeroDataFrame = zeroDataFrame.drop(['index'], axis=1)
		initialDatetime = zeroDataFrame['datetime'][len(zeroDataFrame)-1]
		logger.info(f'{nameTable} is exist! Past datetime: {initialDatetime}')
		newDataFrame = False
	except Exception as error_body:
		logger.info(f'{nameTable} is NO exist...')
		initialDatetime = datetime(2009, 1, 1, 0, 0)
		newDataFrame = True

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
	fullIndexes = pd.date_range(start=zeroDataFrame.index.min(), end=zeroDataFrame.index.max(), freq=timeFramePandas)
	dataFrame = zeroDataFrame.reindex(fullIndexes).ffill()
	dataFrame = dataFrame.reset_index(names=['datetime'])

	dataFrame.to_sql(nameTable, con=engine, if_exists='replace')
	logger.info(f'{nameTable} is saved to dataBaseHistory!')

try:
	main()

except Exception as error_body:
	logger.critical('Critical error!!!', exc_info=True)