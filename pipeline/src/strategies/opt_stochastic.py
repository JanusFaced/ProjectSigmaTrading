from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
import time
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

	train_size, test_size = 4000, 300
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

	divided = 100 #100
	profit_loss = 2.71 #2.71
	maxValueInd, minValueInd = 1.00, 0.00
	degree = 5 #5
	
	target_for_long = profit_loss/(profit_loss+1)
	target_for_short = 1/(profit_loss+1)
	financialReturnName = "futureFinReturn"

	dataFrame = dataFrame.with_columns([
		(pl.col('high')/pl.col('low')-1).alias('statTR'),
	])

	historyATR = float(np.nanmean(dataFrame['statTR'].to_numpy()))

	statsParams = {'historyATR': historyATR}

	for indicatorName in ["signalOscillator", "trendOscillator"]:
		
		fullRangeInd = (maxValueInd - minValueInd)
		bin_width = fullRangeInd/divided
		n_bins = max(int(np.ceil((maxValueInd - minValueInd) / bin_width)), 1)

		tempDF = dataFrame.select([indicatorName, financialReturnName]).drop_nulls().with_columns(
			((pl.col(indicatorName) - minValueInd) / bin_width).floor().clip(0, n_bins - 1).cast(pl.Int32).alias("bin")
		)

		aggDataFrame = tempDF.group_by("bin", maintain_order=True).agg([
			pl.len().alias("count"),
			pl.col(financialReturnName).std().alias("std_y"),
			pl.col(financialReturnName).mean().alias("mean_y"),
		])

		allRangeBins = pl.DataFrame({"bin": list(range(0, divided))})

		aggDF = allRangeBins.join(aggDataFrame, on=["bin"], how="left").with_columns([
			(pl.col('bin')*bin_width + minValueInd).alias("real_x"),
		]).with_columns([
			(pl.col("mean_y") + pl.col("std_y")).alias("up_y"),
			(pl.col("mean_y") - pl.col("std_y")).alias("down_y"),
		])

		for nameYaxis in ['up_y', 'mean_y', 'down_y']:
			x_axis, y_axis, cnt_axis = aggDF["real_x"].to_numpy(), aggDF[nameYaxis].to_numpy(), aggDF["count"].to_numpy()
			x_scaled = 2*(x_axis - minValueInd)/(maxValueInd - minValueInd) - 1

			mask = np.isfinite(x_scaled) & np.isfinite(y_axis) & np.isfinite(cnt_axis) & (cnt_axis > 0)
			x_axis, y_axis, cnt_axis = x_scaled[mask], y_axis[mask], cnt_axis[mask]

			cnt_axis = np.log1p(cnt_axis)

			coeffs = np.polyfit(x_axis, y_axis, degree, w=cnt_axis)
			polyModel = np.poly1d(coeffs)

			y_fit = polyModel(x_scaled)
			aggDF = aggDF.with_columns(pl.Series(f"{nameYaxis}_line", y_fit))

		aggDF = aggDF.with_columns([
			pl.when(
				pl.col("up_y_line") < pl.col("mean_y_line")
			).then(pl.col("mean_y_line")).otherwise(pl.col("up_y_line")).alias("up_y_line"),
			pl.when(
				pl.col("down_y_line") > pl.col("mean_y_line")).then(pl.col("mean_y_line")
			).otherwise(pl.col("down_y_line")).alias("down_y_line"),
		]).with_columns([
			(pl.col("up_y_line") - 0).alias("positivePotential"),
			(0 - pl.col("down_y_line")).alias("negativePotential"),
		]).with_columns([
			(pl.col('positivePotential')/(pl.col('positivePotential') + pl.col('negativePotential'))).alias('potentialMove'),
		])

		for direction in ['long', 'short']:
			target = target_for_long if direction == 'long' else target_for_short
			cond = (pl.col("potentialMove") > target) if direction == "long" else (pl.col("potentialMove") < target)

			workDF = aggDF.with_row_count("i").select(["i", "real_x", "potentialMove"]).with_columns(
				cond.alias("hit")
			)

			workDF = workDF.with_columns(
				pl.when(pl.col("hit") & ~pl.col("hit").shift(1, fill_value=False))
				.then(1)
				.otherwise(0)
				.alias("new_run")
			).with_columns(
				pl.when(pl.col("hit"))
				.then(pl.col("new_run").cum_sum())
				.otherwise(None)
				.alias("run_key")
			)

			outData = workDF.drop_nulls("run_key").group_by("run_key").agg(
				pl.first("i").alias("start"),
				pl.last("i").alias("end"),
				pl.first("real_x").alias("x_start"),
				pl.last("real_x").alias("x_end"),
			).sort("start").select(["x_start", "x_end"]).to_dicts()

			if direction == 'long':
				longDict = [{'start': d['x_start'], 'end': d['x_end']} for d in outData]
			else:
				shortDict = [{'start': d['x_start'], 'end': d['x_end']} for d in outData]

		if len(longDict) == 0:
			longDict = [{'start': maxValueInd, 'end': maxValueInd}]
		else:
			longDict[-1]['end'] = maxValueInd

		if len(shortDict) == 0:
			shortDict = [{'start': minValueInd, 'end': minValueInd}]
		else:
			shortDict[0]['start'] = minValueInd

		if indicatorName == 'signalOscillator':
			statsParams['signalLongFields'] = longDict
			statsParams['signalShortFields'] = shortDict
		elif indicatorName == 'trendOscillator':
			statsParams['trendLongFields'] = longDict
			statsParams['trendShortFields'] = shortDict

	return statsParams

def logicStrategy(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict,
		statsParams: dict
	) -> pl.DataFrame:

	signalUpBoard = statsParams['signalLongFields'][-1]['start']
	signalDownBoard = statsParams['signalShortFields'][0]['end']
	trendLongFields = statsParams['trendLongFields']
	trendShortFields = statsParams['trendShortFields']
	historyATR = statsParams['historyATR']
	
	multiMaxLoss = 3.0*historyATR
	multiMaxProfit = 100.0*historyATR

	trendLogicDict = {}
	series = pl.col("trendOscillator")
	for direction in ["long", "short"]:
		fields = trendLongFields if direction == "long" else trendShortFields
		expr = pl.lit(False)
		for seg in fields:
			expr = expr | ((series >= seg["start"]) & (series <= seg["end"]))
		trendLogicDict[direction] = expr

	dataFrame = dataFrame.with_columns([
		pl.lit(signalUpBoard).alias('signalUpBoard'),
		pl.lit(signalDownBoard).alias('signalDownBoard'),
		pl.lit(-multiMaxLoss).alias('maxLoss'),
		pl.lit(multiMaxProfit).alias('maxProfit'),
	]).with_columns([
		(pl.col('close').shift(1)*(1-multiMaxLoss)).alias('longTrailingStop'),
		(pl.col('close').shift(1)*(1+multiMaxLoss)).alias('shortTrailingStop'),
	]).with_columns([
		pl.when(
			(pl.col('signalOscillator') > signalUpBoard) & (signalUpBoard > pl.col('signalOscillator').shift(1)) &
			trendLogicDict['long']
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
			trendLogicDict['short']
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	])

	return dataFrame





