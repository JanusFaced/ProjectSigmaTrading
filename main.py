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
import json
import requests
import ccxt
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

def dataFrameDownloader(symbol, nameExchange, timeFrame, startYear):
	limit = 1000
	ticker = f'{symbol}/USDT'
	initialDatetime = datetime(startYear, 1, 1, 0, 0)
	
	if nameExchange == 'binance':
		exchange = ccxt.binance()
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()
	
	iso_string = initialDatetime.strftime('%Y-%m-%dT%H:%M:%SZ')
	since = exchange.parse8601(iso_string)
	ohlcv = exchange.fetch_ohlcv(ticker, timeFrame, since, limit)
	dataFrame = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
	dataFrame['datetime'] = dataFrame['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x / 1000))
	dataFrame = dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume']]
	return dataFrame

def main():

	dataFrame = dataFrameDownloader(symbol='BTC', nameExchange='binance', timeFrame='1d', startYear=2024)

	dataFrame['MA'] = dataFrame['close'].rolling(window=10).mean()

	dataFrame['classEDU'] = np.select(
			[
				dataFrame['close'] > dataFrame['MA'],
				dataFrame['close'] < dataFrame['MA']
			],
			[
				-1,
				1
			],
			default=0
		)

	dataFrame['delta'] = (dataFrame['close'] - dataFrame['MA'])/dataFrame['MA']

	uniCut = 365

	datetimeVector = dataFrame['datetime'][-uniCut:]
	closeVector = dataFrame['close'][-uniCut:]
	Y_train = np.array(dataFrame['classEDU'])[-uniCut:]
	X_train = np.array(dataFrame['delta']).reshape(-1, 1)[-uniCut:]

	model = LogisticRegression()
	model.fit(X_train, Y_train)

	Y_edu = model.predict(X_train)

	plt.plot(datetimeVector, closeVector)
	plt.plot(datetimeVector, closeVector*(1+Y_edu/100))
	plt.show()

	logger.info('End!')

try:
	main()

except Exception as error_body:
	logger.critical('Critical error!!!', exc_info=True)

