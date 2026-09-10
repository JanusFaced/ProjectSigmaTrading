import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
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

		if lastName in ['N', 'I']:
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
		
		if strategy == 'hold':
			name_equity = f"{nameExchange}_{symbol}_{type}".lower()
		else:
			name_equity = f"equity_{columnName}"

		try:

			if strategy == 'hold':
				equityDataframe = db.execute(f"SELECT * FROM pg.{name_equity}").pl()
				equityDataframe = equityDataframe[['datetime', 'close']].rename({"close": columnName})

			else:
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

	mask = pl.all_horizontal([pl.col(col).is_not_null() for col in columnNames])

	first_valid_idx = portfolioDF.with_columns(
		mask.alias("all_not_null")
	).select(
		pl.col("all_not_null").arg_true().first()
	).item()

	portfolioDF = portfolioDF.slice(first_valid_idx)

	close_duckdb()
	return portfolioDF, columnNames

def portfolioLogic(
		portfolioDF: pl.DataFrame,
		columnNames: list,
		period_rebalance: int,
		start_depo: float,
		portfolioMode: str,
		modeReBalance: str
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
		start_depo=start_depo,
		modeReBalance=modeReBalance
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

		if endIndex < (fullLenth-1):
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
		start_depo: float,
		modeReBalance: str
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
			modeReBalance=modeReBalance
		)

		listOfDataframes.append(tempDF)

		logger.info(f"----------------------------------------------------")
		logger.info(f"start = {cell['start']} | end = {cell['end']}")
		listAssetWeights = [assetWeights[col] for col in columnNames]
		minWeight = round(np.min(listAssetWeights), 7)
		meanWeight = round(np.mean(listAssetWeights), 7)
		maxWeight = round(np.max(listAssetWeights), 7)
		sumWeight = round(np.sum(listAssetWeights), 7)
		logger.info(f"min = {minWeight} | mean = {meanWeight} | max = {maxWeight} | sum = {sumWeight}")

		if not( minWeight > 0) | (sumWeight > 1):
			raise ValueError(f"exist negative weigths or summa of weigth over one!")

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

	diffBalance = balance[1:] - balance[:-1]
	posDiffBalance = diffBalance[diffBalance > 0]
	negDiffBalance = diffBalance[diffBalance < 0]

	amountProfitDays = len(posDiffBalance)
	amountLossDays = len(negDiffBalance)
	ratioEffectiveDays = yearSize*amountProfitDays/(amountProfitDays+amountLossDays)

	sumProfit = np.sum(posDiffBalance)
	sumLoss = np.sum(negDiffBalance)
	profitFactor = sumProfit/np.abs(sumLoss)

	year_profit = float(round(100*year_profit, 2))
	max_drawdown = float(round(-100*max_drawdown, 2))
	sharp = float(round(sharp, 2))
	calmar = float(round(calmar, 2))
	profit_days = float(round(ratioEffectiveDays, 2))
	profit_factor = float(round(profitFactor, 2))

	optiMetric = (
		year_profit
	)

	analystReport = {
		"year_profit": year_profit,
		"max_drawdown": max_drawdown,
		"sharp": sharp,
		"calmar": calmar,
		"profit_days": profit_days,
		"profit_factor": profit_factor,
		"optiMetric": optiMetric,
	}

	return analystReport

def reBalancer(
		tempDF: pl.DataFrame,
		columnNames: list,
		modeReBalance: str
	) -> dict:

	if modeReBalance == 'simple':
		assetWeights = {col: 1/len(columnNames) for col in columnNames}

	elif modeReBalance == 'profit_zero':
		vectorsDict = {col: tempDF[col].to_numpy() for col in columnNames}
		meanDict = {col: vectorsDict[col][-1]/vectorsDict[col][0] for col in columnNames}
		stdValue = np.mean([meanDict[col] for col in columnNames])
		meanDict = {col: value**np.e if value > 1 else stdValue/100 for col, value in meanDict.items()}
		totalValue = sum(meanDict.values())
		assetWeights = {col: meanDict[col]/totalValue for col in columnNames}

	elif modeReBalance == 'sharp_zero':
		vectorsDict = {col: tempDF[col].to_numpy() for col in columnNames}
		profitDict = {col: vectorsDict[col][-1]/vectorsDict[col][0] for col in columnNames}
		stdDict = {col: np.std(vectorsDict[col]) for col in columnNames}
		sharpDict = {col: profitDict[col]/(stdDict[col]+0.00001) for col in columnNames}
		stdValue = np.mean([sharpDict[col] for col in columnNames])
		sharpDict = {col: sharpDict[col] if profitDict[col] > 1 else stdValue/100 for col in columnNames}
		totalSigma = sum(sharpDict.values())
		assetWeights = {col: sharpDict[col]/totalSigma for col in columnNames}

	elif modeReBalance == 'pf_zero':
		vectorsDict = {col: tempDF[col].to_numpy() for col in columnNames}
		profitDict = {col: vectorsDict[col][-1]/vectorsDict[col][0] for col in columnNames}
		diffsDict = {col: (vectorsDict[col][1:]/vectorsDict[col][:-1] - 1) for col in columnNames}
		posDict = {col: np.sum(diffsDict[col][diffsDict[col] > 0]) for col in columnNames}
		negDict = {col: np.sum(np.abs(diffsDict[col][diffsDict[col] < 0])) for col in columnNames}
		pfDict = {col: posDict[col]/(negDict[col]+0.00001) for col in columnNames}
		stdValue = np.mean([pfDict[col] for col in columnNames])
		pfDict = {col: pfDict[col]**(np.e) if profitDict[col] > 1 else stdValue/100 for col in columnNames}
		totalPF = sum(pfDict.values())
		assetWeights = {col: pfDict[col]/totalPF for col in columnNames}

	return assetWeights


def plotMonteCarlo(
		portfolioDF: pl.DataFrame,
		analystReport: dict
	) -> None:

	balance = portfolioDF['hotDeposite'].to_numpy() + portfolioDF['coldDeposite'].to_numpy()

	simulations = monte_carlo_chunks(
		balance=balance,
		chunk_size=30,
		n_sims=10
	)

	for sim in simulations:
		plt.plot(portfolioDF['datetime'], sim)
	plt.xlabel('Datetime')
	plt.ylabel('Equity')
	plt.title('Different simulations portfolio')
	superName = str(output_dir) + f'/monte_carlo.png'
	plt.savefig(superName)
	plt.close()


	logger.info(" <-[ PORTFOLIO ANALYST ]-> ")
	logger.info(f" @ year_profit   : {analystReport['year_profit']} %")
	logger.info(f" @ max_drawdown  : {analystReport['max_drawdown']} %")
	logger.info(f" @ sharp         : {analystReport['sharp']} ")
	logger.info(f" @ calmar        : {analystReport['calmar']} ")
	logger.info(f" @ profit_factor : {analystReport['profit_factor']} ")
	logger.info(f" @ profit_days   : {analystReport['profit_days']} days/year")
	

	plt.plot(portfolioDF['datetime'], portfolioDF['hotDeposite'], color='orange')
	plt.plot(portfolioDF['datetime'], portfolioDF['coldDeposite'], color='blue')
	plt.xlabel('Datetime')
	plt.ylabel('Equity')
	plt.title('total_equity')
	superName = str(output_dir) + f'/total_equity.png'
	plt.savefig(superName)
	plt.close()


def monte_carlo_chunks(
		balance: npt.NDArray[np.float64],
		chunk_size: int,
		n_sims: int,
	) -> list:

	rng = np.random.default_rng(None)
	balance = np.asarray(balance)

	diffBalance = balance[1:]/balance[:-1]

	n = len(balance)

	chunks = [diffBalance[i:i+chunk_size] for i in range(0, n, chunk_size)]

	sims = []
	for _ in range(n_sims):
		order = rng.permutation(len(chunks))
		sim = np.concatenate([chunks[i] for i in order])
		sims.append(sim)

	finalSims = []
	for sim in sims:
		sim = np.cumprod(sim)*balance[0]
		sim = [balance[0], *sim]
		finalSims.append(sim)

	return finalSims


