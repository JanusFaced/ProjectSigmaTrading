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
		timeFrame: Literal['15min', '30min', '1h', '2h', '4h']
	) -> pd.DataFrame:
	
	nowMuchMoreDays = 300
	maxDelta = 15
	oneDay = 1440
	changeDays = {
		"15min": 15,
		"30min": 35,
		"1h": 75,
		"2h": 150,
		"4h": 300
	}

	amountDays = changeDays[timeFrame]
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
			downloadHistory.main(symbol, nameExchange, nowMuchMoreDays)
			dataFrame = pd.read_sql(queryCode, engine)
			logger.info(f'{nameTable} fetched last {realAmountLines} rows')
	
	except Exception as error_body:
		logger.info(f'{nameTable} does NOT exist. Downloading...')
		downloadHistory.main(symbol, nameExchange, nowMuchMoreDays)
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