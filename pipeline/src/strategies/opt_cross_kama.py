from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
from custom_ta import kamaInd
from pathlib import Path
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	db = get_duckdb()
	dataFrame = db.execute("SELECT * FROM temp_analyst").pl()
	db.execute("DROP TABLE IF EXISTS temp_analyst")

	train_size, test_size = 1000, 300
	quantSlippage = 2000
	generation = 3
	parametrs = {
		"baseWindow": {"min": 20, "max": 200, "split": 5},
	}

	dataFrame = walkForward(
		algorithm=algorithm,
		train_size=train_size,
		test_size=test_size,
		inputMessage=inputMessage,
		originalDataFrame=dataFrame,
		parametrs=parametrs,
		quantSlippage=quantSlippage,
		generation=generation
	)

	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

def algorithm(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict,
		statsParams: dict
	) -> pl.DataFrame:

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	baseWindow = int(params['baseWindow'])
	signalWindow = 1*baseWindow
	trendWindow = 10*baseWindow

	leverage = 1

	multiMaxLoss = 1.0
	multiMaxProfit = 100.0

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		(pl.col('high')/pl.col('low') - 1).rolling_mean(window_size=trendWindow).alias('ATR'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	])

	dataFrame = dataFrame.with_columns([
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
		(pl.lit(multiMaxProfit)*pl.col('ATR')).alias('maxProfit'),
	])

	kamaWindow = int(0.5*signalWindow)

	minWindow, maxWindow = int(0.1*signalWindow), int(1.0*signalWindow)
	fastMIN, fastMAX = 2/(minWindow + 1), 2/(maxWindow + 1)

	minWindow, maxWindow = int(0.2*signalWindow), int(2.0*signalWindow)
	slowMIN, slowMAX = 2/(minWindow + 1), 2/(maxWindow + 1)

	dataFrame = dataFrame.with_columns([
		(pl.col('close') - pl.col('close').shift(kamaWindow)).abs().alias('clearMove'),
		(pl.col('close') - pl.col('close').shift(1)).abs().rolling_sum(window_size=kamaWindow).alias('cumMove'),
	]).with_columns([
		(pl.col('clearMove')/pl.col('cumMove')).rolling_mean(window_size=kamaWindow).alias('ER'),
	]).with_columns([
		(pl.col('ER')*(fastMIN-fastMAX)+fastMAX).alias('fastCoef'),
		(pl.col('ER')*(slowMIN-slowMAX)+slowMAX).alias('slowCoef'),
	])

	fastKAMA = kamaInd(
		closeVector=dataFrame['close'].to_numpy(),
		scVector=dataFrame['fastCoef'].to_numpy(),
		window=int(2*kamaWindow),
	)

	slowKAMA = kamaInd(
		closeVector=dataFrame['close'].to_numpy(),
		scVector=dataFrame['slowCoef'].to_numpy(),
		window=int(2*kamaWindow),
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('fastSignalMoving', fastKAMA),
		pl.Series('slowSignalMoving', slowKAMA),
	])
	
	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('fastSignalMoving') > pl.col('slowSignalMoving')) & (pl.col('slowSignalMoving') > pl.col('fastSignalMoving').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			(pl.col('fastSignalMoving') < pl.col('slowSignalMoving')) & (pl.col('slowSignalMoving') < pl.col('fastSignalMoving').shift(1))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(pl.col('fastSignalMoving') > pl.col('slowSignalMoving')) & (pl.col('slowSignalMoving') > pl.col('fastSignalMoving').shift(1))
		).then(pl.lit(-1))
		.when(
			(pl.col('fastSignalMoving') < pl.col('slowSignalMoving')) & (pl.col('slowSignalMoving') < pl.col('fastSignalMoving').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	)

	statsParams = {}
	return dataFrame, statsParams





