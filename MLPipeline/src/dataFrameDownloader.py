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

def main(
		nameExchange: str,
		symbol: str,
		type: str,
		timeFrame: str,
		mode: str,
		factor: str,
		typeFactor: str,
		factorExchange: str
	) -> pd.DataFrame:

	if factor == 'None':
		dataFrame: pd.DataFrame = downloadDataFrame(
			nameExchange = nameExchange,
			symbol = symbol,
			type = type,
			timeFrame = timeFrame,
			mode = mode,
		)
		dataFrame = resampleDataframe(dataframe=dataFrame, timeframe=timeFrame, factorMode = False)

	elif factor != 'None':
		baseDataFrame: pd.DataFrame = downloadDataFrame(
			nameExchange = nameExchange,
			symbol = symbol,
			type = type,
			timeFrame = timeFrame,
			mode = mode,
		)

		factorDataFrame: pd.DataFrame = downloadDataFrame(
			nameExchange = factorExchange,
			symbol = factor,
			type = typeFactor,
			timeFrame = timeFrame,
			mode = mode,
		)

		dataFrame = tableMerger(baseDataFrame, factorDataFrame)
		dataFrame = resampleDataframe(dataframe=dataFrame, timeframe=timeFrame, factorMode = True)

	return dataFrame

def downloadDataFrame(
		nameExchange: str,
		symbol: str,
		type: str,
		timeFrame: str,
		mode: str,
	) -> pd.DataFrame:

	engine = create_engine(DATABASE_URL)
	inspector = inspect(engine)

	if mode == 'test':
		maxDelta: int = 30
		maxDeltaDatetime = timedelta(days=maxDelta)
		modeMultiple = "identical"
		standartDeep: int = 5_000_000
		#standartDeep: int = 5_000

		if modeMultiple == "identical":
			realAmountLines: int = standartDeep
		elif modeMultiple == "relative":
			realAmountLines: int = standartDeep*convertorTimeFrame(timeFrame)
		
		nameTable: str = f"{nameExchange}_{symbol}_{type}".lower()

	elif mode in ['imitation', 'real']:
		valueConvertor: int = convertorTimeFrame(timeFrame)
		maxDeltaDatetime = timedelta(minutes=valueConvertor)
		standartDeep: int = 3000
		realAmountLines: int = standartDeep*valueConvertor
		nameTable: str = f"short_{nameExchange}_{symbol}_{type}".lower()

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
		else:
			logger.info(f'{nameTable} is fresh :-)')
	
	except Exception as error_body:
		logger.info(f'{nameTable} does NOT exist!')
		downloadData = True

	if downloadData:
		downloadHistory.main(
			nameExchange=nameExchange,
			symbol=symbol,
			type=type,
			mode=mode,
			nowMuchMoreDays=125
		)
		dataFrame = pd.read_sql(queryCode, engine)
		logger.info(f'{nameTable} fetched last {realAmountLines} rows')

	return dataFrame

def resampleDataframe(dataframe: pd.DataFrame, timeframe: str, factorMode: bool) -> pd.DataFrame:
	if factorMode:
		mask = {
			'open': 'first',
			'high': 'max',
			'low': 'min',
			'close': 'last',
			'volume': 'sum',
			'openFactor': 'first',
			'highFactor': 'max',
			'lowFactor': 'min',
			'closeFactor': 'last',
			'volumeFactor': 'sum',
		}
	else:
		mask = {
			'open': 'first',
			'high': 'max',
			'low': 'min',
			'close': 'last',
			'volume': 'sum'
		}
	dataframe.set_index('datetime', inplace=True)
	dataframe = dataframe.resample(timeframe).agg(mask)
	dataframe = dataframe.iloc[:-1]
	dataframe.reset_index(inplace=True)
	return dataframe

def tableMerger(baseDataFrame: pd.DataFrame, factorDataFrame: pd.DataFrame) -> pd.DataFrame:
	columns_to_rename = ['open', 'high', 'low', 'close', 'volume']
	rename_dict = {}
	for col in columns_to_rename:
		if col in factorDataFrame.columns:
			rename_dict[col] = f'{col}Factor'
	factorDataFrame = factorDataFrame.rename(columns=rename_dict)
	dataFrame = pd.merge(
		baseDataFrame,
		factorDataFrame,
		on='datetime',
		how='inner'
	)
	return dataFrame