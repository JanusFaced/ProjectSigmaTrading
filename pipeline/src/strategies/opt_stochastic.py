from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
import time
import os
from walk_forward_simulator import walkForward
from custom_ta import indicatorTuning, volativityTuning
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
	) -> tuple[pl.DataFrame, dict]:

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	volParams = statsParams if statsParams != None else volativityTuning(dataFrame, inputMessage)

	historyATR = volParams['historyATR']
	baseWindow = int(params['baseWindow'])	

	metricsWindow = baseWindow//4
	signalWindow = baseWindow
	trendWindow = 10*baseWindow
	leverage = 3

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		pl.col('close').rolling_max(window_size=signalWindow).alias('sMax'),
		pl.col('close').rolling_min(window_size=signalWindow).alias('sMin'),
		pl.col('close').rolling_max(window_size=trendWindow).alias('tMax'),
		pl.col('close').rolling_min(window_size=trendWindow).alias('tMin'),
	]).with_columns([
		((pl.col('close') - pl.col('sMin'))/(pl.col('sMax') - pl.col('sMin'))).alias('signalOscillator'),
		((pl.col('close') - pl.col('tMin'))/(pl.col('tMax') - pl.col('tMin'))).alias('trendOscillator'),
	]).with_columns([
		((pl.col('open') + pl.col('high') + pl.col('low') + pl.col('close'))/4).alias('price'),
	]).with_columns([
		(pl.col('volume')*pl.col('price')).log1p().alias('convertVolume'),
		pl.col('price').rolling_mean(window_size=metricsWindow).alias('price'),
	]).with_columns([
		pl.col('convertVolume').rolling_mean(window_size=metricsWindow).alias('meanVolume'),
		pl.col('convertVolume').rolling_std(window_size=metricsWindow).alias('stdVolume'),
		(pl.col('price')/pl.col('price').shift(metricsWindow) - 1).alias('pastFinReturn'),
	]).with_columns([
		((pl.col('convertVolume') - pl.col('meanVolume'))/pl.col('stdVolume')).tanh().alias('zScoreVolume'),
		pl.col('pastFinReturn').shift(-metricsWindow).alias('futureFinReturn'),
	])

	indParams = (
		statsParams if statsParams != None else {
			'signal': indicatorTuning(dataFrame, inputMessage, 'signalOscillator', "futureFinReturn"),
			'trend': indicatorTuning(dataFrame, inputMessage, 'trendOscillator', "futureFinReturn")
		}
	)

	signalUpBoard = indParams['signal']['long'][-1]['start']
	signalDownBoard = indParams['signal']['short'][0]['end']
	trendLongFields = indParams['trend']['long']
	trendShortFields = indParams['trend']['short']
	
	multiMaxLoss = 3.0*historyATR
	multiMaxProfit = 100.0*historyATR
	minZscoreVolume = 0.00

	trendLogicDict = {}
	series = pl.col("trendOscillator")
	for direction in ["long", "short"]:
		fields = trendLongFields if direction == "long" else trendShortFields
		expr = pl.lit(False)
		for seg in fields:
			expr = expr | ((series >= seg["start"]) & (series <= seg["end"]))
		trendLogicDict[direction] = expr

	dataFrame = dataFrame.with_columns([
		pl.lit(historyATR).alias('historyATR'),
		pl.lit(baseWindow).alias('baseWindow'),
		pl.lit(-multiMaxLoss).alias('maxLoss'),
		pl.lit(multiMaxProfit).alias('maxProfit'),
	]).with_columns([
		(pl.col('close').shift(1)*(1-multiMaxLoss)).alias('longTrailingStop'),
		(pl.col('close').shift(1)*(1+multiMaxLoss)).alias('shortTrailingStop'),
	]).with_columns([
		pl.when(
			(pl.col('signalOscillator') > signalUpBoard) & (signalUpBoard > pl.col('signalOscillator').shift(1)) &
			trendLogicDict['long'] & (pl.col('zScoreVolume') > minZscoreVolume)
		).then(pl.lit(-1))
		.when(
			((pl.col('signalOscillator') < signalUpBoard) & (signalUpBoard < pl.col('signalOscillator').shift(1))) |
			((pl.col('close') < pl.col('longTrailingStop')) & (pl.col('longTrailingStop') < pl.col('close').shift(1)))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			((pl.col('signalOscillator') > signalDownBoard) & (signalDownBoard > pl.col('signalOscillator').shift(1))) |
			((pl.col('close') > pl.col('shortTrailingStop')) & (pl.col('shortTrailingStop') > pl.col('close').shift(1)))
		).then(pl.lit(-1))
		.when(
			(pl.col('signalOscillator') < signalDownBoard) & (signalDownBoard < pl.col('signalOscillator').shift(1)) &
			trendLogicDict['short'] & (pl.col('zScoreVolume') > minZscoreVolume)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	statsParams = {**volParams, **indParams} if statsParams == None else statsParams
	return dataFrame, statsParams



