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
from sqlalchemy import create_engine

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

dataBase_user = os.getenv('DB_USER', 'postgres')
dataBase_password = os.getenv('DB_PASSWORD', 'postgres')
dataBase_name = os.getenv('DB_NAME', 'postgres')

dataBase_host = os.getenv('DB_HOST', 'dataBase')
dataBase_port = os.getenv('DB_PORT', '5432')

make_logger.make()
logger = logging.getLogger('DATAMINER:dms')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)

def checkConnect():
	logger.info(f"Попытка подключения к БД на хосте: {dataBase_host}...")
	try:
		with engine.connect() as conn:
			result = conn.execute("SELECT 1")
			logger.info("✅ Подключение к базе данных успешно установлено!")
	except Exception as e:
		logger.info(f"❌ Ошибка подключения к БД: {e}")

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

'''
def main():

	dataFrame = dataFrameDownloader(symbol='ETH', nameExchange='binance', timeFrame='1d', startYear=2023)

	windowFeatures0 = 7
	windowFeatures1 = 30
	windowFeatures2 = 90

	centreMoving = 20
	quantile = 0.75

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
			[
				-1,
				1
			],
			default=0
		)

	plt.plot(dataFrame['datetime'], dataFrame['close'])
	plt.plot(dataFrame['datetime'], dataFrame['centreMoving'])
	plt.savefig(str(current_dir/'output'/'plotInd0.png'))
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

	baseModel = DecisionTreeClassifier(random_state=42)

	paramGrid = {
		'max_depth': [3, 4, 5, None],
		'min_samples_split': [2, 3, 4],
		'min_samples_leaf': [1, 2, 3, 4],
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
			  feature_names=['features0', 'features1', 'features2'],
			  class_names=['Buy', 'Sell', 'Wait'],
			  filled=True,
			  rounded=True,
			  fontsize=10)
	plt.title("DecisionTreeClassifier")
	plt.savefig(str(current_dir/'output'/'plot0.png'))
	plt.close()

	yPredict = model.predict(xTrain)
	plt.plot(datetimeTrain, closeTrain)
	plt.plot(datetimeTrain, closeTrain*(1+yPredict/25))
	plt.savefig(str(current_dir/'output'/'plot1.png'))
	plt.close()

	yPredict = model.predict(xTest)
	plt.plot(datetimeTest, closeTest)
	plt.plot(datetimeTest, closeTest*(1+yPredict/25))
	plt.savefig(str(current_dir/'output'/'plot2.png'))
	plt.close()

	logger.info('End!')
'''
def main():
	checkConnect()
	logger.info('End!')

try:
	main()

except Exception as error_body:
	logger.critical('Critical error!!!', exc_info=True)

