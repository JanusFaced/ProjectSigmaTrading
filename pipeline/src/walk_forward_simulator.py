from typing import Callable, Any
from itertools import product
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import os
from fastBackTester import coreBacktester
from trading_simulator import backTestAnalyst
from logger_setup import get_logger

logger = get_logger(__name__)

def walkForward(
		algorithm: Callable[pl.DataFrame, Any],
		train_size: int,
		test_size: int,
		inputMessage: dict,
		originalDataFrame: pl.DataFrame,
		parametrs: dict,
		quantSlippage: int
	) -> pl.DataFrame:

	listIndexes = makeIndexes(
		lenth=len(originalDataFrame),
		train_size=train_size,
		test_size=test_size,
		quantSlippage=quantSlippage
	)

	combiPars = {}
	for namePar, configPar in parametrs.items():
		minValue = configPar['min']
		maxValue = configPar['max']
		splitValue = configPar['split']
		step = int((maxValue - minValue)/(splitValue - 1))
		combiPars[namePar] = list(range(minValue, maxValue, step))

	keys = list(combiPars.keys())
	value_lists = [combiPars[k] for k in keys]

	numberWFcycle = 0
	for indexes in listIndexes:
		trainDataFrame = originalDataFrame[indexes['startTrain']:indexes['endTrain']]
		testDataFrame = originalDataFrame[indexes['startTest']:indexes['endTest']]

		optiList = []
		parsList = []
		for combo in product(*value_lists):
			params = dict(zip(keys, combo))

			dataFrame = algorithm(
				dataFrame=trainDataFrame,
				inputMessage=inputMessage,
				params=params
			)
			report = coreBacktester(dataFrame, inputMessage["testMode"])
			analystReport = backTestAnalyst(
				inputMessage=inputMessage,
				report=report,
				analystMode=True
			)
			optiList.append(analystReport['optiMetric'])
			parsList.append(params)

		bestResult = max(optiList)
		indexBestPars = optiList.index(bestResult)
		bestPars = parsList[indexBestPars]

		#logger.info(f"{numberWFcycle} best result {bestResult} with best pars = {bestPars}")

		tempDataFrame = algorithm(
			dataFrame=testDataFrame,
			inputMessage=inputMessage,
			params=bestPars
		)

		if numberWFcycle == 0:
			finalDataFrame = tempDataFrame

		else:
			last_datetime = finalDataFrame["datetime"].max()
			tempDataFrame = tempDataFrame.filter(pl.col("datetime") >= last_datetime)
			finalDataFrame = pl.concat([finalDataFrame, tempDataFrame])

		numberWFcycle += 1

	return finalDataFrame

@njit(cache=True)
def makeIndexes(
		lenth: int,
		train_size: int,
		test_size: int,
		quantSlippage: int
	) -> dict:
	listIndexes = []

	index = quantSlippage
	while True:
		startTrain = index - quantSlippage
		endTrain = index + train_size
		startTest = endTrain - quantSlippage
		endTest = endTrain + test_size
		
		if (lenth - startTest) > test_size:

			listIndexes.append({
				"startTrain": startTrain,
				"endTrain": endTrain,
				"startTest": startTest,
				"endTest": endTest,
			})
			index += test_size

		else:
			break

	return listIndexes