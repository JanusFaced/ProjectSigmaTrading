from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
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

	signalUpBoard = 0.80
	signalDownBoard = 0.20

	multiMaxLoss = 1.0
	multiMaxProfit = 100.0

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		(pl.col('high')/pl.col('low') - 1).rolling_mean(window_size=trendWindow).alias('ATR'),
		pl.col('close').rolling_max(window_size=signalWindow).alias('sMax'),
		pl.col('close').rolling_min(window_size=signalWindow).alias('sMin'),
	]).with_columns([
		((pl.col('close') - pl.col('sMin'))/(pl.col('sMax') - pl.col('sMin'))).alias('signalOscillator'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	])

	dataFrame = dataFrame.with_columns([
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
		(pl.lit(multiMaxProfit)*pl.col('ATR')).alias('maxProfit'),
	])

	dataFrame = dataFrame.with_columns([
		pl.when(
			(pl.col('signalOscillator') > signalUpBoard) & (signalUpBoard > pl.col('signalOscillator').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			((pl.col('signalOscillator') < signalUpBoard) & (signalUpBoard < pl.col('signalOscillator').shift(1)))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			((pl.col('signalOscillator') > signalDownBoard) & (signalDownBoard > pl.col('signalOscillator').shift(1)))
		).then(pl.lit(-1))
		.when(
			(pl.col('signalOscillator') < signalDownBoard) & (signalDownBoard < pl.col('signalOscillator').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	statsParams = {}
	return dataFrame, statsParams





