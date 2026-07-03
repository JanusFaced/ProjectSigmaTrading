from typing import Literal, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
from sqlalchemy import create_engine, inspect
import downloadHistory
from convertorTF import convertorTimeFrame
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
		nameExchange: str,
		symbol: str,
		type: str,
		timeFrame: str,
		mode: str,
		maxDelta: int = 30
	) -> pd.DataFrame:
	
	engine = create_engine(DATABASE_URL)
	inspector = inspect(engine)

	maxDeltaDatetime = timedelta(days=maxDelta)
	
	modeMultiple = "identical"
	standartDeep: int = 1000000

	if modeMultiple == "identical":
		realAmountLines: int = standartDeep
	elif modeMultiple == "relative":
		realAmountLines: int = standartDeep*convertorTimeFrame(timeFrame)
	
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
		nameExchange: str,
		symbol: str, 
		type: str,
		timeFrame: str,
		mode: str,
		nowMuchMoreDays: int = 75,
		maxDelta: int = 15
	) -> pd.DataFrame:
	
	maxDeltaDatetime = timedelta(minutes=maxDelta)
	standartDeep: int = 1440
	amountDays: int = convertorTimeFrame(timeFrame)
	realAmountLines: int = standartDeep*amountDays
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