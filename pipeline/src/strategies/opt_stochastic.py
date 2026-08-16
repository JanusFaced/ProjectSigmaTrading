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

	train_size, test_size = 2000, 300
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
	trendWindow = 5*baseWindow

	leverage = 1

	multiMaxLoss = 1.0
	multiMaxProfit = 100.0

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		((pl.col('high')/pl.col('low'))-1).rolling_mean(window_size=trendWindow).alias('ATR'),
		pl.col('close').rolling_max(window_size=signalWindow).alias('sMax'),
		pl.col('close').rolling_min(window_size=signalWindow).alias('sMin'),
		pl.col('close').rolling_max(window_size=trendWindow).alias('tMax'),
		pl.col('close').rolling_min(window_size=trendWindow).alias('tMin'),
	]).with_columns([
		((pl.col('close') - pl.col('sMin'))/(pl.col('sMax') - pl.col('sMin'))).alias('signalOscillator'),
		((pl.col('close') - pl.col('tMin'))/(pl.col('tMax') - pl.col('tMin'))).alias('trendOscillator'),
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
		inputMessage: dict,
		params: dict
	) -> dict:

	baseWindow = int(params['baseWindow'])

	try:
		divided = 100
		profit_loss = 3.0
		maxLongInd, minLongInd = 1.00, 0.55
		maxShortInd, minShortInd = 0.45, 0.00
		degree = 3
		
		target_for_long = profit_loss/(profit_loss+1)
		target_for_short = 1/(profit_loss+1)
		financialReturnName = "futureFinReturn"

		statsParams = {}
		for indicatorName in ["signalOscillator", "trendOscillator"]:
			tempDF = dataFrame.select([indicatorName, financialReturnName]).drop_nulls()

			x_min = float(tempDF[indicatorName].min())
			x_max = float(tempDF[indicatorName].max())

			fullRangeInd = (x_max - x_min)
			bin_width = fullRangeInd/divided

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
				coeffs = np.polyfit(x_axis, y_axis, degree)
				polyModel = np.poly1d(coeffs)
				y_fit = polyModel(aggDF["mean_x"].to_numpy())

				nameLine = f"{nameYaxis}_line"
				aggDF = aggDF.with_columns(pl.Series(nameLine, y_fit))

			aggDF = aggDF.with_columns([
				(pl.col("up_y_line") - 0).alias("positivePotential"),
				(0 - pl.col("down_y_line")).alias("negativePotential"),
			]).with_columns([
				(pl.col('positivePotential')/(pl.col('positivePotential') + pl.col('negativePotential'))).alias('potentialMove'),
			])

			maxMeanX = np.max(aggDF['mean_x'].to_numpy())
			minMeanX = np.min(aggDF['mean_x'].to_numpy())

			maxValuePotential = np.max(aggDF['potentialMove'].to_numpy())
			minValuePotential = np.min(aggDF['potentialMove'].to_numpy())

			if maxValuePotential > target_for_long:
				if maxMeanX > minLongInd:
					long_bins = aggDF.filter(pl.col("potentialMove") >= target_for_long)
					long_bins_2 = long_bins.sort("mean_x")
					long_bins_3 = long_bins_2.filter(pl.col("mean_x") >= minLongInd)
					if len(long_bins_3) > 0:
						long_threshold = long_bins_3.select(pl.col("mean_x").min()).item()
						upBoard = float(long_threshold) if float(long_threshold) > minLongInd else minLongInd
					else:
						upBoard = maxLongInd
				else:
					upBoard = maxLongInd
			else:
				upBoard = maxLongInd
			
			if minValuePotential < target_for_short:
				if minMeanX < maxShortInd:
					short_bins = aggDF.filter(pl.col("potentialMove") <= target_for_short)
					short_bins_2 = short_bins.sort("mean_x")
					short_bins_3 = short_bins_2.filter(pl.col("mean_x") <= maxShortInd)
					if len(short_bins_3) > 0:
						short_threshold = short_bins_3.select(pl.col("mean_x").max()).item()
						downBoard = float(short_threshold) if float(short_threshold) < maxShortInd else maxShortInd
					else:
						downBoard = minShortInd
				else:
					downBoard = minShortInd
			else:
				downBoard = minShortInd

			if indicatorName == 'signalOscillator':
				statsParams['signalUpBoard'] = upBoard
				statsParams['signalDownBoard'] = downBoard
			elif indicatorName == 'trendOscillator':
				statsParams['trendUpBoard'] = upBoard
				statsParams['trendDownBoard'] = downBoard

	except Exception as e:
		logger.info(f"error: {e}")

		logger.info(f"baseWindow={baseWindow} | lenth DF= {len(dataFrame)}")

		plt.plot(dataFrame['trendOscillator'], color='red')
		superName = str(output_dir) + f'/1.png'
		plt.savefig(superName)
		plt.close()

		plt.plot(tempDF)
		superName = str(output_dir) + f'/2.png'
		plt.savefig(superName)
		plt.close()

		superName = str(output_dir) + f'/3.png'
		plt.plot(aggDF['mean_x'], aggDF['up_y'], color='red')
		plt.plot(aggDF['mean_x'], aggDF['mean_y'], color='black')
		plt.plot(aggDF['mean_x'], aggDF['down_y'], color='green')
		plt.savefig(superName)
		plt.close()

		superName = str(output_dir) + f'/4.png'
		plt.plot(aggDF['mean_x'], aggDF['up_y_line'], color='red')
		plt.plot(aggDF['mean_x'], aggDF['mean_y_line'], color='black')
		plt.plot(aggDF['mean_x'], aggDF['down_y_line'], color='green')
		plt.savefig(superName)
		plt.close()

		superName = str(output_dir) + f'/5.png'
		plt.plot(aggDF['mean_x'], aggDF['potentialMove'], color='black')
		plt.savefig(superName)
		plt.close()

	return statsParams

def logicStrategy(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict,
		statsParams: dict
	) -> pl.DataFrame:

	signalUpBoard = statsParams['signalUpBoard']
	signalDownBoard = statsParams['signalDownBoard']
	trendUpBoard = statsParams['trendUpBoard']
	trendDownBoard = statsParams['trendDownBoard']

	dataFrame = dataFrame.with_columns([
		pl.lit(signalUpBoard).alias('signalUpBoard'),
		pl.lit(signalDownBoard).alias('signalDownBoard'),
		pl.lit(trendUpBoard).alias('trendUpBoard'),
		pl.lit(trendDownBoard).alias('trendDownBoard'),
	]).with_columns([
		pl.when(
			(pl.col('signalOscillator') > signalUpBoard) & (signalUpBoard > pl.col('signalOscillator').shift(1)) &
			(pl.col('trendOscillator') > trendUpBoard)
		).then(pl.lit(-1))
		.when(
			(
				((pl.col('signalOscillator') < signalUpBoard) & (signalUpBoard < pl.col('signalOscillator').shift(1))) |
				((pl.col('close') < pl.col('longTrailingStop')) & (pl.col('longTrailingStop') < pl.col('close').shift(1)))
			)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(
				((pl.col('signalOscillator') > signalDownBoard) & (signalDownBoard > pl.col('signalOscillator').shift(1))) |
				((pl.col('close') > pl.col('shortTrailingStop')) & (pl.col('shortTrailingStop') > pl.col('close').shift(1)))
			)
		).then(pl.lit(-1))
		.when(
			(pl.col('signalOscillator') < signalDownBoard) & (signalDownBoard < pl.col('signalOscillator').shift(1)) &
			(pl.col('trendOscillator') < trendDownBoard)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	return dataFrame





