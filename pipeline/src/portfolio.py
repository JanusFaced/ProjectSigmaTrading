import polars as pl
import numpy as np
import sys
import os
import makeStats
from portfolio_tools import getEquity, portfolioLogic, portfolioAnalyst, plotMonteCarlo
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)

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

	portfolioDF = portfolioLogic(
		portfolioDF=portfolioDF,
		columnNames=columnNames,
		period_rebalance=360,
		start_depo=100.00,
		portfolioMode=portfolioMode,
		modeReBalance='profit_zero' #simple profit_zero sharp_zero pf_zero
	)

	analystReport = portfolioAnalyst(
		dataframe=portfolioDF,
		portfolioMode=portfolioMode
	)

	plotMonteCarlo(portfolioDF, analystReport)


