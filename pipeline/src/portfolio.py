import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import sys
import os
from duckDB_setup import get_duckdb, close_duckdb
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"

def main(portfolioParams: dict) -> None:
	portfolioName = portfolioParams['portfolioName']
	assetsList = portfolioParams['assetsList']

	portfolioDF, columnNames = getEquity(assetsList)

	portfolioDF = portfolioDF.with_columns(pl.sum_horizontal(columnNames).alias("total_equity"))
	
	
	'''
	for col in columnNames:
		plt.plot(portfolioDF['datetime'], portfolioDF[col], label=col)
	plt.legend()
	plt.xlabel('Datatime')
	plt.ylabel('Equity')
	plt.title('Different assets in portfolio')
	superName = str(output_dir) + f'/assets_{portfolioName}.png'
	plt.savefig(superName)
	plt.close()
	'''


	plt.plot(portfolioDF['datetime'], portfolioDF['total_equity'])
	plt.xlabel('Datatime')
	plt.ylabel('Equity')
	plt.title('total_equity')
	superName = str(output_dir) + f'/total_equity_{portfolioName}.png'
	plt.savefig(superName)
	plt.close()

def getEquity(assetsList: dict) -> tuple[pl.DataFrame, list]:
	db = get_duckdb()

	portfolioDF = []
	for asset in assetsList:

		nameStrategy = asset["strategy"]
		splitNameStrategy = nameStrategy.split(":")
		firstName = splitNameStrategy[0]
		lastName = splitNameStrategy[1]

		if lastName == 'I':
			asset['strategy'] = firstName

		elif lastName == 'II':
			asset['strategy'] = ":".join([
				firstName,
				asset['factor'],
				asset['typeFactor'],
				asset['factorExchange']
			])

		strategy = asset['strategy']
		symbol = asset['symbol']
		timeFrame = asset['timeFrame']
		type = asset['type']
		nameExchange = asset['nameExchange']

		columnName = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"
		name_equity = f"equity_{columnName}"

		try:
			equityDataframe = db.execute(f'SELECT * FROM pg."{name_equity}"').pl()

			equityDataframe = equityDataframe.sort("datetime").group_by_dynamic(
				index_column="datetime",
				every="1d",
				period="1d",
				closed="left",
				label="left"
			).agg([
				pl.col(columnName).last()
			]).with_columns(
				pl.col(columnName).fill_null(strategy="forward")
			)

			portfolioDF = (
				equityDataframe if len(portfolioDF) == 0
				else portfolioDF.join(equityDataframe, on="datetime", how="outer", coalesce=True)
			)
			logger.info(f' : Equity {name_equity} is GET from DataBase!')

		except Exception as e:
			logger.error(f' >< ERROR. Equty {name_equity} NOT get!...')
			logger.error(f'error: {e}')
		
	portfolioDF = portfolioDF.sort("datetime")
	columnNames = [x for x in portfolioDF.columns if x != "datetime"]
	
	for col in columnNames:
		portfolioDF = portfolioDF.with_columns(pl.col(col).fill_null(strategy="forward"))

	close_duckdb()
	return portfolioDF, columnNames