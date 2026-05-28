from typing import Literal, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
import ccxt
from sqlalchemy import create_engine
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

	logger.info(f'Start save {nameTable} in dataBase!')
	zeroDataFrame.to_sql(nameTable, con=engine, if_exists='replace', chunksize=5000, method='multi')
	logger.info(f'{nameTable} is saved to dataBase!')