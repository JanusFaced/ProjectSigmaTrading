from typing import Literal, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
import ccxt
from sqlalchemy import create_engine, inspect
from logger_setup import get_logger

logger = get_logger(__name__)

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)

def main(
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		symbol: str,
		type: str,
		mode: str,
		nowMuchMoreDays: int = 365
	) -> pd.DataFrame:

	if mode == 'test':
		dataFrame: pd.DataFrame = backTime(
			nameExchange=nameExchange,
			symbol=symbol,
			type=type
		)
	
	elif mode in ['imitation', 'real']:
		dataFrame: pd.DataFrame = inTime(
			nameExchange=nameExchange,
			symbol=symbol,
			type=type,
			nowMuchMoreDays=nowMuchMoreDays
		)

	return dataFrame

def backTime(
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		symbol: str,
		type: str
	) -> None:

	engine = create_engine(DATABASE_URL)
	inspector = inspect(engine)

	if nameExchange == 'binance':
		exchange = ccxt.binance()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'
	
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
		if type == 'futures':
			exchange.options['defaultType'] = 'linear'

	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'

	elif nameExchange == 'okx':
		exchange = ccxt.okx()
		exchange.options['defaultType'] = 'swap'
	
	elif nameExchange == 'bitget':
		exchange = ccxt.bitget()
		exchange.options['defaultType'] = 'swap'

	else:
		raise ValueError(f"Неизвестная биржа: {nameExchange}")

	nameTable: str = f"{nameExchange}_{symbol}_{type}".lower()

	if type == 'spot':
		ticker: str = f'{symbol}/USDT'
	elif type == 'futures':
		ticker: str = f'{symbol}/USDT:USDT'

	timeFrame: str = '1m'
	timeFramePandas: str = '1min'
	deltaDatetime = timedelta(minutes=1)
	stepDatetime = timedelta(days=30)
	limit: int = 1000
	
	queryCode: str = f"""
		SELECT * FROM {nameTable}
	"""

	newDataFrame: bool = False
	if nameTable in inspector.get_table_names():
		zeroDataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} is exist! Get full table!')
		initialDatetime = zeroDataFrame['datetime'].iloc[-1]
	
	else:
		logger.info(f'{nameTable} does NOT exist!')
		initialDatetime = datetime(2017, 1, 1)
		newDataFrame = True


	logger.info(f' >>> START {nameTable} <<< ')

	while True:

		getData = False
		while getData == False:

			iso_string = initialDatetime.strftime('%Y-%m-%dT%H:%M:%SZ')
			since = exchange.parse8601(iso_string)
			
			try:
				ohlcv = exchange.fetch_ohlcv(ticker, timeFrame, since, limit)

				if ohlcv:
					logger.info('get!')
					getData = True
				else:
					logger.info('fail...')
					initialDatetime = initialDatetime + stepDatetime
					logger.info(f'try parsing from new initialDatetime => {initialDatetime}')

			except Exception as e:
				logger.info(f'Ошибка {e}. Ожидаем 5 секунд...')
				time.sleep(5)

		dataFrame = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
		dataFrame['datetime'] = dataFrame['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x / 1000))
		dataFrame = dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume']]
		initialDatetime = dataFrame['datetime'].iloc[-1]
		
		if newDataFrame:
			zeroDataFrame = dataFrame.copy()
			newDataFrame = False
		else:
			zeroDataFrame = pd.concat([zeroDataFrame, dataFrame], ignore_index=True)

		nowDatetime = datetime.utcnow()
		logger.info(f"{nameTable} <=> {initialDatetime}")
		if initialDatetime >= (nowDatetime - deltaDatetime):
			break

	zeroDataFrame['datetime'] = pd.to_datetime(zeroDataFrame['datetime'])
	zeroDataFrame.set_index('datetime', inplace=True)
	zeroDataFrame = zeroDataFrame[~zeroDataFrame.index.duplicated(keep='first')]
	
	min_date = zeroDataFrame.index.min()
	max_date = zeroDataFrame.index.max()
	fullIndexes = pd.date_range(start=min_date, end=max_date, freq=timeFramePandas)
	zeroDataFrame = zeroDataFrame.reindex(fullIndexes).ffill()
	
	zeroDataFrame.reset_index(inplace=True, names=['datetime'])

	logger.info(f'Start save {nameTable} in dataBase!')
	zeroDataFrame.to_sql(nameTable, con=engine, if_exists='replace', chunksize=5000, method='multi')
	logger.info(f'{nameTable} is saved to dataBase!')

def inTime(
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		symbol: str,
		type: str,
		nowMuchMoreDays: int = 365
	) -> None:

	if nameExchange == 'binance':
		exchange = ccxt.binance()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'
	
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
		if type == 'futures':
			exchange.options['defaultType'] = 'linear'

	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'

	elif nameExchange == 'okx':
		exchange = ccxt.okx()
		exchange.options['defaultType'] = 'swap'
	
	elif nameExchange == 'bitget':
		exchange = ccxt.bitget()
		exchange.options['defaultType'] = 'swap'

	else:
		raise ValueError(f"Неизвестная биржа: {nameExchange}")

	nameTable: str = f"short_{nameExchange}_{symbol}_{type}".lower()

	if type == 'spot':
		ticker: str = f'{symbol}/USDT'
	elif type == 'futures':
		ticker: str = f'{symbol}/USDT:USDT'

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
		if initialDatetime >= (nowDatetime - deltaDatetime):
			break

	zeroDataFrame['datetime'] = pd.to_datetime(zeroDataFrame['datetime'])
	zeroDataFrame.set_index('datetime', inplace=True)
	zeroDataFrame = zeroDataFrame[~zeroDataFrame.index.duplicated(keep='first')]
	
	min_date = zeroDataFrame.index.min()
	max_date = zeroDataFrame.index.max()
	fullIndexes = pd.date_range(start=min_date, end=max_date, freq=timeFramePandas)
	zeroDataFrame = zeroDataFrame.reindex(fullIndexes).ffill()
	
	zeroDataFrame.reset_index(inplace=True, names=['datetime'])

	logger.info(f'Start save {nameTable} in dataBase!')
	zeroDataFrame.to_sql(nameTable, con=engine, if_exists='replace', chunksize=5000, method='multi')
	logger.info(f'{nameTable} is saved to dataBase!')