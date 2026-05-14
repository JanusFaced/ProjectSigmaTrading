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
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

'''
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

	window_ma = 10
	window_roc = 100

	dataFrame['MA'] = dataFrame['close'].rolling(window=window_ma).mean()
	dataFrame['delta'] = (dataFrame['close'] - dataFrame['MA'])/dataFrame['MA']

	dataFrame['ROC'] = (dataFrame['close'] - dataFrame['close'].shift(window_roc))/dataFrame['close'].shift(window_roc)

	dataFrame['classEDU'] = np.select(
			[
				(dataFrame['delta'] > 0) & (dataFrame['ROC'] > 0),
				(dataFrame['delta'] < 0) & (dataFrame['ROC'] < 0)
			],
			[
				-1,
				1
			],
			default=0
		)

	workDataFrame = dataFrame.iloc[window_roc:]

	uniCut = int(len(workDataFrame)/2)

	datetimeTrain = workDataFrame['datetime'][:uniCut]
	closeTrain = workDataFrame['close'][:uniCut]
	yTrain = np.array(workDataFrame['classEDU'])[:uniCut]
	vectorF0 = np.array(workDataFrame['delta']).reshape(-1, 1)[:uniCut]
	vectorF1 = np.array(workDataFrame['ROC']).reshape(-1, 1)[:uniCut]
	xTrain = np.column_stack((vectorF0, vectorF1))

	datetimeTest = workDataFrame['datetime'][uniCut:]
	closeTest = workDataFrame['close'][uniCut:]
	yTest = np.array(workDataFrame['classEDU'])[uniCut:]
	vectorF0 = np.array(workDataFrame['delta']).reshape(-1, 1)[uniCut:]
	vectorF1 = np.array(workDataFrame['ROC']).reshape(-1, 1)[uniCut:]
	xTest = np.column_stack((vectorF0, vectorF1))

	baseModel = DecisionTreeClassifier(random_state=42)

	paramGrid = {
		'max_depth': [3, 5, 10, None],
		'min_samples_split': [2, 5, 10],
		'min_samples_leaf': [1, 2, 4],
		'criterion': ['gini', 'entropy'],
		'max_features': [None, 'sqrt', 'log2']
	}

	gridSearch = GridSearchCV(
		estimator=baseModel,
		param_grid=paramGrid,
		cv=5,                    # 5-кратная кросс-валидация
		scoring='accuracy',      # метрика качества
		n_jobs=-1,              # используем все ядра процессора
		verbose=1               # показываем прогресс
	)

	gridSearch.fit(xTrain, yTrain)
	model = gridSearch.best_estimator_

	plt.figure(figsize=(12, 8))
	plot_tree(model, 
			  feature_names=['delta', 'ROC'],
			  class_names=['Buy', 'Wait', 'Sell'],
			  filled=True,
			  rounded=True,
			  fontsize=10)
	plt.title("DecisionTreeClassifier")
	plt.show()


	yPredict = model.predict(xTrain)
	plt.plot(datetimeTrain, closeTrain)
	plt.plot(datetimeTrain, closeTrain*(1+yPredict/100))
	plt.show()

	yPredict = model.predict(xTest)
	plt.plot(datetimeTest, closeTest)
	plt.plot(datetimeTest, closeTest*(1+yPredict/100))
	plt.show()

	logger.info('End!')
'''

def main():

	for _ in range(10):
		logger.info("In programm!")

try:
	main()

except Exception as error_body:
	logger.critical('Critical error!!!', exc_info=True)

