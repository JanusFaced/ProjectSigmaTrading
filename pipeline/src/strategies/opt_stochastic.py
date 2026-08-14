from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
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

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	train_size, test_size = 1000, 300
	quantSlippage = 2000
	generation = 3
	parametrs = {
		"baseWindow": {"min": 20, "max": 200, "split": 5},
	}

	dataFrame = walkForward(
		featuresMaker=featuresMaker,
		statsFitting=statsFitting,
		logicStrategy=logicStrategy,
		train_size=train_size,
		test_size=test_size,
		inputMessage=inputMessage,
		originalDataFrame=dataFrame,
		parametrs=parametrs,
		quantSlippage=quantSlippage,
		generation=generation
	)

	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

def featuresMaker(
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
	metricsWindow = baseWindow//4
	signalWindow = baseWindow
	trendWindow = 10*baseWindow

	leverage = 1

	multiMaxLoss = 1.0
	multiMaxProfit = 100.0

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		((pl.col('high')/pl.col('low'))-1).rolling_mean(window_size=trendWindow).alias('ATR'),
		pl.col('close').rolling_max(window_size=signalWindow).alias('sMax'),
		pl.col('close').rolling_min(window_size=signalWindow).alias('sMin'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	]).with_columns([
		((pl.col('close') - pl.col('sMin'))/(pl.col('sMax') - pl.col('sMin'))).alias('oscillator'),
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
		(pl.lit(multiMaxProfit)*pl.col('ATR')).alias('maxProfit'),
	]).with_columns([
		(pl.col('close').shift(1)*(1+pl.col('maxLoss'))).alias('longTrailingStop'),
		(pl.col('close').shift(1)*(1-pl.col('maxLoss'))).alias('shortTrailingStop'),
	]).with_columns([
		((pl.col('open') + pl.col('high') + pl.col('low') + pl.col('close'))/4).alias('price'),
	]).with_columns([
		pl.col('price').rolling_mean(window_size=metricsWindow).alias('price'),
	]).with_columns([
		(pl.col('price')/pl.col('price').shift(metricsWindow) - 1).alias('pastFinReturn'),
	]).with_columns([
		pl.col('pastFinReturn').shift(-metricsWindow).alias('futureFinReturn'),
	])

	return dataFrame

def statsFitting(
		dataFrame: pl.DataFrame,
		inputMessage: dict
	) -> dict:

	indicatorName = "oscillator"
	financialReturnName = "futureFinReturn"
	bin_width = 0.01

	tempDF = dataFrame.select([indicatorName, financialReturnName]).drop_nulls()

	x_min = float(tempDF[indicatorName].min())
	x_max = float(tempDF[indicatorName].max())

	n_bins = int(np.ceil((x_max - x_min) / bin_width))
	n_bins = max(n_bins, 1)

	cutDF = tempDF.with_columns(
		((pl.col(indicatorName) - x_min) / bin_width).floor().clip(0, n_bins - 1).cast(pl.Int32).alias("bin")
	).drop_nulls(["bin"])

	aggDF = cutDF.group_by("bin", maintain_order=True).agg([
		pl.len().alias("count"),
		pl.col(indicatorName).mean().alias("mean_x"),
		pl.col(financialReturnName).min().alias("min_y"),
		pl.col(financialReturnName).std().alias("std_y"),
		pl.col(financialReturnName).mean().alias("mean_y"),
		pl.col(financialReturnName).max().alias("max_y"),
	]).sort("bin").with_columns([
		(pl.col("mean_y") + pl.col("std_y")).alias("up_y"),
		(pl.col("mean_y") - pl.col("std_y")).alias("down_y"),
	])

	for nameYaxis in ['up_y', 'mean_y', 'down_y']:
		x_axis, y_axis = aggDF["mean_x"].to_numpy(), aggDF[nameYaxis].to_numpy()
		mask = np.isfinite(x_axis) & np.isfinite(y_axis)
		x_axis, y_axis = x_axis[mask], y_axis[mask]
		a_par, b_par = np.polyfit(x_axis, y_axis, 1)

		aggDF = aggDF.with_columns([
			(a_par*pl.col("mean_x") + b_par).alias(f"{nameYaxis}_line"),
		])

	aggDF = aggDF.with_columns([
		(pl.col("up_y_line") - 0).alias("positivePotential"),
		(0 - pl.col("down_y_line")).alias("negativePotential"),
	]).with_columns([
		(pl.col('positivePotential')/(pl.col('positivePotential') + pl.col('negativePotential'))).alias('potentialMove'),
	])

	maxValuePotential = np.max(aggDF['potentialMove'].to_numpy())
	minValuePotential = np.min(aggDF['potentialMove'].to_numpy())

	target_for_long = 0.75
	target_for_short = 0.25

	if maxValuePotential > target_for_long:
		long_bins = aggDF.filter(pl.col("potentialMove") >= target_for_long).sort("mean_x")
		long_threshold = long_bins.select(pl.col("mean_x").min()).item()
		upBoard = float(long_threshold)
	else:
		upBoard = 0.95
	
	if minValuePotential < target_for_short:
		short_bins = aggDF.filter(pl.col("potentialMove") <= target_for_short).sort("mean_x")
		short_threshold = short_bins.select(pl.col("mean_x").max()).item()
		downBoard = float(short_threshold)
	else:
		downBoard = 0.05

	statsParams = {
		'upBoard': upBoard,
		'downBoard': downBoard,
	}

	return statsParams

def logicStrategy(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict,
		statsParams: dict
	) -> pl.DataFrame:

	upBoard = statsParams['upBoard']
	downBoard = statsParams['downBoard']

	dataFrame = dataFrame.with_columns([
		pl.lit(upBoard).alias('upBoard'),
		pl.lit(downBoard).alias('downBoard'),
	]).with_columns([
		pl.when(
			(pl.col('oscillator') > upBoard) & (upBoard > pl.col('oscillator').shift(1)) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			(
				((pl.col('oscillator') < upBoard) & (upBoard < pl.col('oscillator').shift(1))) |
				((pl.col('close') < pl.col('longTrailingStop')) & (pl.col('longTrailingStop') < pl.col('close').shift(1)))
			) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(
				((pl.col('oscillator') > downBoard) & (downBoard > pl.col('oscillator').shift(1))) |
				((pl.col('close') > pl.col('shortTrailingStop')) & (pl.col('shortTrailingStop') > pl.col('close').shift(1)))
			) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(-1))
		.when(
			(pl.col('oscillator') < downBoard) & (downBoard < pl.col('oscillator').shift(1)) &
			(pl.col('close') < pl.col('trendMoving'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	return dataFrame





