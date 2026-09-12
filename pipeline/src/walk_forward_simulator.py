from typing import Callable, Any
from itertools import product
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import json
import os
import copy
from fastBackTester import coreBacktester
from trading_simulator import backTestAnalyst
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)

output_dir = Path(__file__).parent / "output"
config_dir = Path(__file__).parent / "config"

def walkForward(
		algorithm: Callable[pl.DataFrame, Any],
		train_size: int,
		test_size: int,
		inputMessage: dict,
		originalDataFrame: pl.DataFrame,
		parametrs: dict,
		quantSlippage: int,
		generation: int
	) -> pl.DataFrame:

	listIndexes = makeIndexes(
		lenth=len(originalDataFrame),
		train_size=train_size,
		test_size=test_size,
		quantSlippage=quantSlippage
	)

	numberWFcycle = 0
	for indexes in listIndexes:
		trainDataFrame = originalDataFrame[indexes['startTrain']:indexes['endTrain']]
		testDataFrame = originalDataFrame[indexes['startTest']:indexes['endTest']]

		
		if len(parametrs) > 0:
			tempParametrs = copy.deepcopy(parametrs)
			for gen in range(generation):

				combiPars = {}
				for namePar, configPar in tempParametrs.items():
					minValue = configPar['min']
					maxValue = configPar['max']
					splitValue = configPar['split']
					typeValue = configPar['typeData']

					if typeValue == "noFix":
						step = (maxValue - minValue)/(splitValue - 1)
						combiPars[namePar] = [minValue + i*step for i in range(splitValue)]

					elif typeValue == "Fix":
						combiPars[namePar] = [x for x in range(minValue, maxValue+1)]


				keys = list(combiPars.keys())
				value_lists = [combiPars[k] for k in keys]

				optiList = []
				parsList = []
				statParsList = []
				for combo in product(*value_lists):
					params = dict(zip(keys, combo))

					backtestDataFrame, statsParams = algorithm(
						dataFrame=trainDataFrame,
						inputMessage=inputMessage,
						params=params,
						statsParams=None
					)
					report = coreBacktester(backtestDataFrame, inputMessage["testMode"])
					analystReport = backTestAnalyst(
						inputMessage=inputMessage,
						report=report,
						analystMode=True
					)
					optiList.append(analystReport['optiMetric'])
					parsList.append(params)

					statParsList.append(statsParams)

				bestResult = max(optiList)
				indexBestPars = optiList.index(bestResult)
				bestPars = parsList[indexBestPars]
				bestStatsParams = statParsList[indexBestPars]

				for namePar, valuePar in bestPars.items():
					minValue = tempParametrs[namePar]['min']
					maxValue = tempParametrs[namePar]['max']
					splitValue = tempParametrs[namePar]['split']
					typeValue = tempParametrs[namePar]['typeData']

					if typeValue == 'noFix':
						step = (maxValue - minValue)/(splitValue - 1)
						tempParametrs[namePar]['max'] = valuePar + step if valuePar != maxValue else maxValue
						tempParametrs[namePar]['min'] = valuePar - step if valuePar != minValue else minValue

					elif typeValue == 'Fix':
						tempParametrs[namePar]['max'] = valuePar
						tempParametrs[namePar]['min'] = valuePar

		else:
			_, statsParams = algorithm(
				dataFrame=trainDataFrame,
				inputMessage=inputMessage,
				params=parametrs,
				statsParams=None
			)
			bestPars, bestStatsParams = parametrs, statsParams

		tempDataFrame, _ = algorithm(
			dataFrame=testDataFrame,
			inputMessage=inputMessage,
			params=bestPars,
			statsParams=bestStatsParams
		)

		if numberWFcycle == 0:
			finalDataFrame = tempDataFrame

		else:
			last_datetime = finalDataFrame["datetime"].max()
			tempDataFrame = tempDataFrame.filter(pl.col("datetime") >= last_datetime)
			finalDataFrame = pl.concat([finalDataFrame, tempDataFrame])

		numberWFcycle += 1

	finalPars = copy.deepcopy(bestPars)
	finalStatsParams = copy.deepcopy(bestStatsParams)

	saveWorkParams(
		finalPars=finalPars,
		finalStatsParams=finalStatsParams,
		inputMessage=inputMessage
	)

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
		
		if (lenth - endTrain) > test_size:

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

def saveWorkParams(
		finalPars: dict,
		finalStatsParams: dict,
		inputMessage: str,
	) -> None:

	strategy = inputMessage['strategy']
	symbol = inputMessage['symbol']
	timeFrame = inputMessage['timeFrame']
	type = inputMessage['type']
	nameExchange = inputMessage['nameExchange']

	name = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"
	fileName: str = f'{config_dir}/work_parametrs/{name}.json'
	
	params = {"finalPars": finalPars, "finalStatsParams": finalStatsParams,}

	with open(fileName, 'w', encoding='utf-8') as f:
		json.dump(params, f, indent=4, ensure_ascii=False)
	
	logger.info(f" ✏️ Parametrs for {fileName} was saved!")

def getWorkParams(
		inputMessage: str,
	) -> tuple[dict, dict]:

	strategy = inputMessage['strategy']
	symbol = inputMessage['symbol']
	timeFrame = inputMessage['timeFrame']
	type = inputMessage['type']
	nameExchange = inputMessage['nameExchange']

	name = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"

	fileName: str = f'{config_dir}/work_parametrs/{name}.json'

	with open(fileName, "r", encoding="utf-8") as f:
		params = json.load(f)

	finalPars = params['finalPars']
	finalStatsParams = params['finalStatsParams']

	logger.info(f" ⬆️ Parametrs for {fileName} was get!")

	return finalPars, finalStatsParams
