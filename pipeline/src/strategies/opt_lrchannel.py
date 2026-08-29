from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
from custom_ta import simple_linear_regression
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

	multiMaxLoss = 2.00

	lrcurve = simple_linear_regression(
		closeVector=dataFrame['close'].to_numpy(),
		baseWindow=signalWindow
	)

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		(pl.col('high')/pl.col('low') - 1).rolling_mean(window_size=trendWindow).alias('ATR'),
		pl.Series('lrcurve', lrcurve),
		pl.col('close').rolling_std(window_size=signalWindow).alias('sigma'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	]).with_columns([
		(pl.col('lrcurve') + pl.col('sigma')).alias('signalMovingUpLine'),
		(pl.col('lrcurve') - pl.col('sigma')).alias('signalMovingDownLine'),
	]).with_columns([
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
	]).with_columns(
		pl.when(
			(pl.col('close') > pl.col('signalMovingUpLine')) & (pl.col('signalMovingUpLine') > pl.col('close').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			(pl.col('close') < pl.col('signalMovingUpLine')) & (pl.col('signalMovingUpLine') < pl.col('close').shift(1))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(pl.col('close') > pl.col('signalMovingDownLine')) & (pl.col('signalMovingDownLine') > pl.col('close').shift(1))
		).then(pl.lit(-1))
		.when(
			(pl.col('close') < pl.col('signalMovingDownLine')) & (pl.col('signalMovingDownLine') < pl.col('close').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	)

	statsParams = {}
	return dataFrame, statsParams





