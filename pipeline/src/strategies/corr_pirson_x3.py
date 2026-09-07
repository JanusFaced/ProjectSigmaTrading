from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
from custom_ta import spreadMaker
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
		"baseWindow": {"min": 20, "max": 200, "split": 5, "typeData": "noFix"},
		"multiMaxLoss": {"min": 1.0, "max": 5.0, "split": 5, "typeData": "noFix"},
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

	leverage = 3

	multiMaxLoss = params['multiMaxLoss']

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		(pl.col('high')/pl.col('low') - 1).rolling_mean(window_size=trendWindow).alias('ATR'),
	])

	spread = spreadMaker(
		secondaryVector=dataFrame['close'].to_numpy(),
		primaryVector=dataFrame['closeFactor'].to_numpy(),
		baseWindow=signalWindow
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('spread', spread),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
		pl.col('close').rolling_mean(window_size=signalWindow).alias('guideLine'),
	]).with_columns([
		(pl.col('guideLine')/pl.col('guideLine').shift(1) - 1).alias('stepMaxLoss'),
	]).with_columns([
		pl.col('spread').rolling_mean(window_size=signalWindow).alias('averageSpread'),
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
	]).with_columns([
		(pl.col('spread') - pl.col('averageSpread')).abs().rolling_mean(window_size=signalWindow).alias('deltaSpread'),
	]).with_columns([
		( pl.col('deltaSpread') + pl.col('deltaSpread') ).alias('maxBoard'),
		( pl.col('deltaSpread') - pl.col('deltaSpread') ).alias('minBoard'),
	]).with_columns([
		pl.when(
			(pl.col('spread') > pl.col('maxBoard')) & (pl.col('maxBoard') > pl.col('spread').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			(pl.col('spread') < pl.col('maxBoard')) & (pl.col('maxBoard') < pl.col('spread').shift(1))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(pl.col('spread') > pl.col('minBoard')) & (pl.col('minBoard') > pl.col('spread').shift(1))
		).then(pl.lit(-1))
		.when(
			(pl.col('spread') < pl.col('minBoard')) & (pl.col('minBoard') < pl.col('spread').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	statsParams = {}
	return dataFrame, statsParams





