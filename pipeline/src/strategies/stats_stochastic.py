from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
import time
import os
from walk_forward_simulator import walkForward
from custom_ta import volativityTuning
from pathlib import Path
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	db = get_duckdb()
	dataFrame = db.execute("SELECT * FROM temp_analyst").pl()
	db.execute("DROP TABLE IF EXISTS temp_analyst")

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	train_size, test_size = 4000, 300
	quantSlippage = 2000

	dataFrame = walkForward(
		algorithm=algorithm,
		train_size=train_size,
		test_size=test_size,
		inputMessage=inputMessage,
		originalDataFrame=dataFrame,
		parametrs={},
		quantSlippage=quantSlippage,
		generation=1
	)

	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

def algorithm(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict,
		statsParams: dict
	) -> tuple[pl.DataFrame, dict]:

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	signalWindow = 20
	trendWindow = 200
	leverage = 1

	statsParams = (
		statsParams if statsParams != None
		else volativityTuning(
			dataFrame,
			inputMessage,
		)
	)

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		pl.col('close').rolling_max(window_size=signalWindow).alias('sMax'),
		pl.col('close').rolling_min(window_size=signalWindow).alias('sMin'),
	]).with_columns([
		((pl.col('close') - pl.col('sMin'))/(pl.col('sMax') - pl.col('sMin'))).alias('signalOscillator'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	])

	historyATR = statsParams['historyATR']

	signalUpBoard = 0.80
	signalDownBoard = 0.20

	multiMaxLoss = 1.5

	dataFrame = dataFrame.with_columns([
		pl.lit(-1).alias('maxLoss'),
		pl.lit(100).alias('maxProfit'),
	]).with_columns([
		(pl.col('close').shift(1)*(1+multiMaxLoss*historyATR)).alias('shortTrailingStop'),
		(pl.col('close').shift(1)*(1-multiMaxLoss*historyATR)).alias('longTrailingStop'),
	]).with_columns([
		pl.when(
			(pl.col('signalOscillator') > signalUpBoard) & (signalUpBoard > pl.col('signalOscillator').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			#(
			#	(pl.col('signalOscillator') < signalUpBoard) & (signalUpBoard < pl.col('signalOscillator').shift(1))
			#) |
			(
				(pl.col('close') < pl.col('longTrailingStop')) & (pl.col('longTrailingStop') < pl.col('close').shift(1))
			)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			#(
			#	(pl.col('signalOscillator') > signalDownBoard) & (signalDownBoard > pl.col('signalOscillator').shift(1))
			#) |
			(
				(pl.col('close') > pl.col('shortTrailingStop')) & (pl.col('shortTrailingStop') > pl.col('close').shift(1))
			)
		).then(pl.lit(-1))
		.when(
			(pl.col('signalOscillator') < signalDownBoard) & (signalDownBoard < pl.col('signalOscillator').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	return dataFrame, statsParams



