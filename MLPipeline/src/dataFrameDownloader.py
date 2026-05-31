from typing import Literal, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import sys
from sqlalchemy import create_engine
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

def main(
		symbol: str, 
		nameExchange: Literal['binance', 'bybit', 'kucoin'],
		timeFrame: Literal['15min', '30min', '1h'],
		nowMuchMoreDays: int = 75,
		maxDelta: int = 15
	) -> pd.DataFrame:
	
	maxDeltaDatetime = timedelta(minutes=maxDelta)
	changeDays: dict = {
		"15min": 15,
		"30min": 35,
		"1h": 75
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
			symbol=symbol,
			nameExchange=nameExchange,
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