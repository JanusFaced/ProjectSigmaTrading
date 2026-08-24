import polars as pl
import numpy as np
import sys
import os
import time
from duckDB_setup import get_duckdb, close_duckdb
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"

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

def portfolioLogic(
		portfolioDF: pl.DataFrame,
		columnNames: list,
		period_rebalance: int,
		start_depo: float,
		portfolioMode: str = 'cumul'
	) -> pl.DataFrame:

	fullLenth = len(portfolioDF)
	amountAssets = len(columnNames)
	start_depo = start_depo/amountAssets

	baseWeights = 1/amountAssets
	assetWeights = {col: baseWeights for col in columnNames}

	portfolioDF = reIntegral(
		dataframe=portfolioDF,
		columnNames=columnNames,
		start_depo=start_depo,
		assetWeights=assetWeights
	)

	listOfIndexes = makeIndexes(
		fullLenth=fullLenth,
		period_rebalance=period_rebalance
	)

	portfolioDF = portfolioManager(
		dataframe=portfolioDF,
		columnNames=columnNames,
		listOfIndexes=listOfIndexes,
		portfolioMode=portfolioMode,
		start_depo=start_depo
	)

	finalPortfolioDF = portfolioDF.with_columns(pl.sum_horizontal(columnNames).alias("hotDeposite"))
	return finalPortfolioDF

def reIntegral(
		dataframe: pl.DataFrame,
		columnNames: list,
		start_depo: float,
		assetWeights: dict
	) -> pl.DataFrame:

	diff_exprs = [
		(pl.col(col)/pl.col(col).shift(1)).fill_null(1).alias(f"{col}_diff")
		for col in columnNames
	]
	integrate_prod = [
		(pl.col(f"{col}_diff").cum_prod()).alias(f"{col}_prod")
		for col in columnNames
	]
	integrate_depo = [
		(pl.col(f"{col}_prod")*pl.lit(start_depo*assetWeights[col])).alias(col)
		for col in columnNames
	]
	drop_cols = [
		*[f"{col}_diff" for col in columnNames],
		*[f"{col}_prod" for col in columnNames]
	]

	dataframe = dataframe.with_columns(diff_exprs).with_columns(integrate_prod).with_columns(integrate_depo).drop(drop_cols)
	return dataframe

def makeIndexes(
		fullLenth: int,
		period_rebalance: int
	) -> list:

	index = 0
	listOfIndexes = []
	while True:
		startIndex = index
		endIndex = index + period_rebalance

		if endIndex < fullLenth:
			listOfIndexes.append({
				'start': startIndex,
				'end': endIndex,
			})
			index += period_rebalance
		
		else:
			listOfIndexes.append({
				'start': startIndex,
				'end': fullLenth-1,
			})
			break
		
	return listOfIndexes

def portfolioManager(
		dataframe: pl.DataFrame,
		columnNames: int,
		listOfIndexes: list,
		portfolioMode: str,
		start_depo: float
	) -> pl.DataFrame:

	listOfDataframes = []
	currentCumule = 0.00
	amountAssets = len(columnNames)
	baseSizeDeposite = start_depo*amountAssets
	currentSumHotDeposite = baseSizeDeposite
	baseWeights = 1/amountAssets
	assetWeights = {col: baseWeights for col in columnNames}

	for cell in listOfIndexes:
		startIndex = cell['start']
		endIndex = cell['end']

		tempDF = dataframe[startIndex:endIndex].with_columns([
			pl.lit(currentCumule).alias('coldDeposite')
		])

		tempDF = reIntegral(
			dataframe=tempDF,
			columnNames=columnNames,
			start_depo=currentSumHotDeposite,
			assetWeights=assetWeights
		)

		tempDF = tempDF.with_columns([
			pl.sum_horizontal(columnNames).alias("SumHotDeposite")
		])

		currentSumHotDeposite = float(tempDF["SumHotDeposite"].to_numpy()[-1])

		if portfolioMode == 'cumul':
			cumule = currentSumHotDeposite - baseSizeDeposite
			if cumule > 0:
				currentCumule += cumule
				currentSumHotDeposite = baseSizeDeposite

		assetWeights = reBalancer(
			tempDF=tempDF,
			columnNames=columnNames,
			modeWork='profit'
		)

		listOfDataframes.append(tempDF)

	finalDataFrame = pl.concat(listOfDataframes)
	return finalDataFrame

def portfolioAnalyst(
		dataframe: pl.DataFrame,
		portfolioMode: str
	) -> dict:

	hot_balance = dataframe['hotDeposite'].to_numpy()
	cold_balance = dataframe['coldDeposite'].to_numpy()
	balance = hot_balance + cold_balance

	mask, hotMask, coldMask = np.isfinite(balance), np.isfinite(hot_balance), np.isfinite(cold_balance)
	balance, hot_balance, cold_balance = balance[mask], hot_balance[mask], cold_balance[mask]

	fullLenth = len(balance)
	yearSize = 365
	amoutSplit = int(fullLenth/yearSize)

	splitBalance = np.array_split(balance, amoutSplit)

	diffVector = [(x[-1]/x[0]-1) for x in splitBalance]

	year_profit = np.mean(diffVector)
	stdYearProfit = np.std(diffVector)
	sharp = year_profit/stdYearProfit

	max_accum = np.maximum.accumulate(hot_balance)
	max_accum = np.clip(max_accum, a_min=None, a_max=hot_balance[0]) if portfolioMode == 'cumul' else max_accum
	drawdowns = (max_accum - hot_balance)/max_accum
	max_drawdown = np.max(drawdowns)	

	calmar = year_profit/max_drawdown

	year_profit = float(round(100*year_profit, 2))
	max_drawdown = float(round(-100*max_drawdown, 2))
	sharp = float(round(sharp, 2))
	calmar = float(round(calmar, 2))

	optiMetric = (
		year_profit
	)

	analystReport = {
		"year_profit": year_profit,
		"max_drawdown": max_drawdown,
		"sharp": sharp,
		"calmar": calmar,
		"optiMetric": optiMetric
	}

	return analystReport

def reBalancer(
		tempDF: pl.DataFrame,
		columnNames: list,
		modeWork: str
	) -> dict:

	if modeWork == 'simple':
		assetWeights = {col: 1/len(columnNames) for col in columnNames}

	elif modeWork == 'profit':
		vectorsDict = {col: tempDF[col].to_numpy() for col in columnNames}
		meanDict = {col: 1/((vectorsDict[col][-1]/vectorsDict[col][0]) + 0.001) for col in columnNames}
		totalMean = sum(meanDict.values())
		assetWeights = {col: meanDict[col]/totalMean for col in columnNames}

	elif modeWork == 'sigma':
		stdDict = {col: 1/(np.std(vectorsDict[col]) + 0.001) for col in columnNames}
		totalSigma = sum(stdDict.values())
		assetWeights = {col: stdDict[col]/totalSigma for col in columnNames}

	return assetWeights
