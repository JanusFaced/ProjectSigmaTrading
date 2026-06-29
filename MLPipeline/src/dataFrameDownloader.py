from typing import Literal, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
from sqlalchemy import create_engine, inspect
import downloadHistory
from logger_setup import get_logger

logger = get_logger(__name__)

dataBase_password = os.getenv('DB_PASSWORD')
dataBase_user = os.getenv('DB_USER')
dataBase_name = os.getenv('DB_NAME')
dataBase_host = os.getenv('DB_HOST')
dataBase_port = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"
engine = create_engine(DATABASE_URL)

def main(inputMessage: dict) -> pd.DataFrame:

	if inputMessage['mode'] == 'test':
		dataFrame: pd.DataFrame = backTime(
			nameExchange=inputMessage['nameExchange'],
			symbol=inputMessage['symbol'],
			type=inputMessage['type'],
			timeFrame=inputMessage['timeFrame'],
			mode=inputMessage['mode']
		)
	
	elif inputMessage['mode'] in ['imitation', 'real']:
		dataFrame: pd.DataFrame = inTime(
			symbol=inputMessage['symbol'],
			nameExchange=inputMessage['nameExchange'],
			type=inputMessage['type'],
			timeFrame=inputMessage['timeFrame'],
			mode=inputMessage['mode']
		)

	return dataFrame

def backTime(
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		symbol: str,
		type: str,
		timeFrame: Literal['1min', '2min', '4min', '8min', '15min', '30min', '1h', '2h', '4h', '6h', '8h', '12h', '1d'],
		mode: str,
		maxDelta: int = 30
	) -> pd.DataFrame:
	
	engine = create_engine(DATABASE_URL)
	inspector = inspect(engine)

	maxDeltaDatetime = timedelta(days=maxDelta)
	
	modeMultiple = "relative"
	commonMultiple: int = 3
	standartDeep: int = 1440

	if modeMultiple == "identical":
		multiple: dict = {
			"1min": 1440*commonMultiple,
			"2min": 1440*commonMultiple,
			"4min": 1440*commonMultiple,
			"8min": 1440*commonMultiple,
			"15min": 1440*commonMultiple,
			"30min": 1440*commonMultiple,
			"1h": 1440*commonMultiple,
			"2h": 1440*commonMultiple,
			"4h": 1440*commonMultiple,
			"6h": 1440*commonMultiple,
			"8h": 1440*commonMultiple,
			"12h": 1440*commonMultiple,
			"1d": 1440*commonMultiple
		}
	elif modeMultiple == "relative":
		multiple: dict = {
			"1min": 1*commonMultiple,
			"2min": 2*commonMultiple,
			"4min": 4*commonMultiple,
			"8min": 8*commonMultiple,
			"15min": 15*commonMultiple,
			"30min": 30*commonMultiple,
			"1h": 60*commonMultiple,
			"2h": 120*commonMultiple,
			"4h": 240*commonMultiple,
			"6h": 360*commonMultiple,
			"8h": 480*commonMultiple,
			"12h": 720*commonMultiple,
			"1d": 1440*commonMultiple
		}
	realAmountLines: int = standartDeep*multiple[timeFrame]
	nameTable: str = f"{nameExchange}_{symbol}_{type}".lower()

	queryCode: str = f"""
		SELECT * FROM (
			SELECT * FROM {nameTable}
			ORDER BY datetime DESC
			LIMIT {realAmountLines}
		) AS last_rows
		ORDER BY datetime ASC
	"""

	logger.info(f"{nameTable}")

	downloadData: bool = False
	if nameTable in inspector.get_table_names():
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} is exist! Fetched last {realAmountLines} rows')
		pastDatetime = dataFrame['datetime'].iloc[-1]
		nowDatetime = datetime.utcnow()
		if (nowDatetime - pastDatetime) > maxDeltaDatetime:
			logger.info(f'{nameTable} is very old!')
			downloadData = True

		else:
			logger.info(f'{nameTable} is fresh :-)')
	
	else:
		logger.info(f'{nameTable} does NOT exist!')
		downloadData = True

	if downloadData:
		downloadHistory.main(
			nameExchange=nameExchange,
			symbol=symbol,
			type=type,
			mode=mode,
			nowMuchMoreDays=None
		)
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} fetched last {realAmountLines} rows')

	dataFrame = resampleDataframe(dataframe=dataFrame, timeframe=timeFrame)

	return dataFrame

def inTime(
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		symbol: str, 
		type: str,
		timeFrame: Literal['1min', '2min', '4min', '8min', '15min', '30min', '1h', '2h', '4h', '6h', '8h', '12h', '1d'],
		mode: str,
		nowMuchMoreDays: int = 75,
		maxDelta: int = 15
	) -> pd.DataFrame:
	
	maxDeltaDatetime = timedelta(minutes=maxDelta)
	commonMultiple: int = 3
	changeDays: dict = {
		"1min": 1*commonMultiple,
		"2min": 2*commonMultiple,
		"4min": 4*commonMultiple,
		"8min": 8*commonMultiple,
		"15min": 15*commonMultiple,
		"30min": 30*commonMultiple,
		"1h": 60*commonMultiple,
		"2h": 120*commonMultiple,
		"4h": 240*commonMultiple,
		"6h": 360*commonMultiple,
		"8h": 480*commonMultiple,
		"12h": 720*commonMultiple,
		"1d": 1440*commonMultiple
	}
	oneDay: int = 1440
	amountDays: int = changeDays[timeFrame]
	realAmountLines: int = oneDay*amountDays
	nameTable: str = f"{nameExchange}_{symbol}".lower()

	queryCode: str = f"""
		SELECT * FROM (
			SELECT * FROM {nameTable}
			ORDER BY datetime DESC
			LIMIT {realAmountLines}
		) AS last_rows
		ORDER BY datetime ASC
	"""

	downloadData: bool = False
	try:
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} is exist! Fetched last {realAmountLines} rows')
		pastDatetime = dataFrame['datetime'].iloc[-1]
		nowDatetime = datetime.utcnow()
		if (nowDatetime - pastDatetime) > maxDeltaDatetime:
			logger.info(f'{nameTable} is very old!')
			downloadData = True
	
	except Exception as error_body:
		logger.info(f'{nameTable} does NOT exist!')
		downloadData = True

	if downloadData:
		downloadHistory.main(
			nameExchange=nameExchange,
			symbol=symbol,
			type=type,
			mode=mode,
			nowMuchMoreDays=nowMuchMoreDays
		)
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} fetched last {realAmountLines} rows')

	dataFrame = resampleDataframe(dataframe=dataFrame, timeframe=timeFrame)

	return dataFrame

def resampleDataframe(dataframe: pd.DataFrame, timeframe: str) -> pd.DataFrame:

	dataframe.set_index('datetime', inplace=True)
	dataframe = dataframe.resample(timeframe).agg({
		'open': 'first',
		'high': 'max',
		'low': 'min',
		'close': 'last',
		'volume': 'sum'
	})
	dataframe.reset_index(inplace=True)

	return dataframe