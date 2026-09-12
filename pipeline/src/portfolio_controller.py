from typing import Callable, Any
from itertools import product
from datetime import datetime, timedelta
import polars as pl
import numpy as np
import numpy.typing as npt
import json
import os
import copy
import saveToDB
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)

output_dir = Path(__file__).parent / "output"
config_dir = Path(__file__).parent / "config"

def main() -> None:

	name_portfolio = "standart"

	receiveList = saveToDB.receive_portfolio(name_portfolio)

	if receiveList['exist']:
		portfolio = receiveList["portfolio"]
		full_profit = receiveList["full_profit"]
		year_profit = receiveList["year_profit"]
		max_drawdown = receiveList["max_drawdown"]
		sharp = receiveList["sharp"]
		profit_factor = receiveList["profit_factor"]
		dataBaseDateTime = receiveList["datetime"]

		copyJSON, originalJSON, identical = parserJSON(exist=True)
		portfolio = parserPortfolio(copyJSON)

		if identical == False:
			logger.info('Not identical!!!')

			reBalance(portfolio, originalJSON)
			saveJSON(originalJSON)

	else:
		dataBaseDateTime = None

		_, originalJSON, _ = parserJSON(exist=False)
		portfolio = 100.00
		reBalance(portfolio, originalJSON)
		saveJSON(originalJSON)

	if dataBaseDateTime != None:
		if ((datetime.now() - dataBaseDateTime) > timedelta(days=1)):
			signalPuck = {"portfolio": portfolio,}
			saveToDB.send_history_portfolio(name_portfolio, signalPuck)
			dataBaseDateTime = datetime.now()

		portfolioVector = getChartOfPortfolio(name_portfolio)

		report = portfolioAnalyst(portfolioVector)

		full_profit = report['full_profit']
		year_profit = report['year_profit']
		max_drawdown =report['max_drawdown']
		sharp = report['sharp']
		profit_factor = report['profit_factor']

	else:
		full_profit = 0.0
		year_profit = 0.0
		max_drawdown = 0.0
		sharp = 0.0
		profit_factor = 1.0
		dataBaseDateTime = datetime.now()

	signalPuck = {
		"portfolio": portfolio,
		"full_profit": full_profit,
		"year_profit": year_profit,
		"max_drawdown": max_drawdown,
		"sharp": sharp,
		"profit_factor": profit_factor,
		"dataBaseDateTime": dataBaseDateTime,
	}

	saveToDB.send_portfolio(name_portfolio, signalPuck)

def parserJSON(exist: bool) -> tuple[dict, dict, bool]:

	if exist:

		fileName: str = f'{config_dir}/work_strats_copy.json'
		with open(fileName, "r", encoding="utf-8") as f:
			work_strats_copy = json.load(f)

		fileName: str = f'{config_dir}/asset_weights_copy.json'
		with open(fileName, "r", encoding="utf-8") as f:
			asset_weights_copy = json.load(f)

		copyJSON = {
			"work_strats_copy": work_strats_copy,
			"asset_weights_copy": asset_weights_copy,
		}

		logger.info(f" ⬆️ copyJSON was get!")

	else:
		copyJSON = {}	


	fileName: str = f'{config_dir}/work_strats.json'
	with open(fileName, "r", encoding="utf-8") as f:
		work_strats = json.load(f)

	fileName: str = f'{config_dir}/asset_weights.json'
	with open(fileName, "r", encoding="utf-8") as f:
		asset_weights = json.load(f)

	originalJSON = {
		"work_strats": work_strats,
		"asset_weights": asset_weights,
	}

	logger.info(f" ⬆️ originalJSON was get!")

	identical = (asset_weights_copy == asset_weights) if exist else False

	return copyJSON, originalJSON, identical


def parserPortfolio(copyJSON: dict) -> float:

	work_strats_copy = copyJSON['work_strats_copy']
	asset_weights_copy = copyJSON['asset_weights_copy']

	listOfStrats = [name for name, value in asset_weights_copy.items()]

	portfolio = saveToDB.parser_portfolio(listOfStrats)

	return portfolio

def reBalance(
		portfolio: float,
		originalJSON: dict
	) -> None:

	work_strats = originalJSON['work_strats']
	asset_weights = originalJSON['asset_weights']

	saveToDB.rebalance_portfolio(portfolio, asset_weights)


def saveJSON(originalJSON: dict) -> None:

	work_strats_copy = originalJSON['work_strats']
	asset_weights_copy = originalJSON['asset_weights']

	fileName: str = f'{config_dir}/work_strats_copy.json'
	with open(fileName, 'w', encoding='utf-8') as f:
		json.dump(work_strats_copy, f, indent=4, ensure_ascii=False)
	
	fileName: str = f'{config_dir}/asset_weights_copy.json'
	with open(fileName, 'w', encoding='utf-8') as f:
		json.dump(asset_weights_copy, f, indent=4, ensure_ascii=False)

	logger.info(f" ✏️ work_strats_copy and asset_weights_copy was saved!")

def getChartOfPortfolio(name_portfolio) -> npt.NDArray[np.float64]:
	vector = saveToDB.get_chart_portfolio(name_portfolio)
	return vector

def portfolioAnalyst(portfolioVector: npt.NDArray[np.float64]) -> dict:

	lenth = len(portfolioVector)

	if lenth > 5:
		full_profit = round(100*(portfolioVector[-1]/portfolioVector[0] - 1), 2)
		year_profit = 365*(full_profit/lenth)
		max_drawdown = round(100*(np.min(portfolioVector)/portfolioVector[0] - 1), 2)
		sharp = round(full_profit/np.std(portfolioVector), 2)
		profit_factor = 1.0

	else:
		full_profit = 0.00
		year_profit = 0.00
		max_drawdown = 0.00
		sharp = 0.00
		profit_factor = 1.0

	report = {
		"full_profit": full_profit,
		"year_profit": year_profit,
		"max_drawdown": max_drawdown,
		"sharp": sharp,
		"profit_factor": profit_factor,
	}

	return report