import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import sys
import os
import makeStats
from portfolio_tools import getEquity, portfolioLogic, portfolioAnalyst
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"

def main(portfolioParams: dict) -> None:
	portfolioName = portfolioParams['portfolioName']
	portfolioMode = portfolioParams['portfolioMode']

	listTimeFrame = portfolioParams['listTimeFrame']
	listStrategy = portfolioParams['listStrategy']
	listSymbol = portfolioParams['listSymbol']
	listFactor = portfolioParams['listFactor']

	assetsList = portfolioParams['assetsList']

	makeStats.main(
		listTimeFrame=listTimeFrame,
		listStrategy=listStrategy,
		listSymbol=listSymbol,
		listFactor=listFactor,
	)

	portfolioDF, columnNames = getEquity(assetsList)

	makeStats.makeCorrelationMap(
		portfolioDF=portfolioDF,
		columnNames=columnNames,
	)

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

	portfolioDF = portfolioLogic(
		portfolioDF=portfolioDF,
		columnNames=columnNames,
		period_rebalance=365,
		start_depo=100.00,
		portfolioMode=portfolioMode,
		modeReBalance='sharp' #simple profit sigma sharp fun_profit
	)

	analystReport = portfolioAnalyst(
		dataframe=portfolioDF,
		portfolioMode=portfolioMode
	)

	logger.info(" <-[ PORTFOLIO ANALYST ]-> ")
	logger.info(f" @ year_profit  : {analystReport['year_profit']} %")
	logger.info(f" @ max_drawdown : {analystReport['max_drawdown']} %")
	logger.info(f" @ sharp        : {analystReport['sharp']} ")
	logger.info(f" @ calmar       : {analystReport['calmar']} ")
	
	plt.plot(portfolioDF['datetime'], portfolioDF['hotDeposite'], color='orange')
	plt.plot(portfolioDF['datetime'], portfolioDF['coldDeposite'], color='blue')
	plt.xlabel('Datatime')
	plt.ylabel('Equity')
	plt.title('total_equity')
	superName = str(output_dir) + f'/total_equity_{portfolioName}.png'
	plt.savefig(superName)
	plt.close()
