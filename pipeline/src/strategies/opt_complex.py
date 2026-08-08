from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
from custom_ta import simple_correlation
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
	parametrs = {
		"numberAlgo": {"min": 0, "max": 11, "split": 12},
		"signalWindow": {"min": 20, "max": 200, "split": 5},
	}

	dataFrame = walkForward(
		algorithm=algorithm,
		train_size=train_size,
		test_size=test_size,
		inputMessage=inputMessage,
		originalDataFrame=dataFrame,
		parametrs=parametrs,
		quantSlippage=quantSlippage
	)

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'leverage'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

def algorithm(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict
	) -> pl.DataFrame:

	numberAlgo = params['numberAlgo']
	signalWindow = params['signalWindow']
	trendWindow = 10*signalWindow
	
	leverage = 1

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	])

	listOfAlgos = [
		"moving",
		"cross_ma",
		"trend",
		"stochastic",
		"bollinger",
		"keltner",
		"envelopes",
		"modeling",
		"correlation",
		"lrcurve",
		"lrchannel",
	]
	algo = listOfAlgos[numberAlgo]

	if algo == "moving":
		dataFrame = dataFrame.with_columns([
			pl.col('close').rolling_mean(window_size=signalWindow).alias('signalMoving'),
		])

		longLogic = (pl.col('close') > pl.col('signalMoving'))
		shortLogic = (pl.col('close') < pl.col('signalMoving'))

	elif algo == "cross_ma":
		fastSignalWindow = signalWindow
		slowSignalWindow = 2*signalWindow

		dataFrame = dataFrame.with_columns([
			pl.col('close').rolling_mean(window_size=fastSignalWindow).alias('fastSignalMoving'),
			pl.col('close').rolling_mean(window_size=slowSignalWindow).alias('slowSignalMoving'),
		])

		longLogic = (pl.col('fastSignalMoving') > pl.col('slowSignalMoving'))
		shortLogic = (pl.col('fastSignalMoving') < pl.col('slowSignalMoving'))

	elif algo == "trend":
		dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(signalWindow) - 1).alias('signalROC'))
		longLogic = (pl.col('signalROC') > 0)
		shortLogic = (pl.col('signalROC') < 0)

	elif algo == "stochastic":
		maxValue = 0.80
		minValue = 0.20

		dataFrame = dataFrame.with_columns([
			pl.col('close').rolling_max(window_size=signalWindow).alias('signalUpLine'),
			pl.col('close').rolling_min(window_size=signalWindow).alias('signalDownLine'),
		])

		dataFrame = dataFrame.with_columns([
			((pl.col('close') - pl.col('signalDownLine'))/(pl.col('signalUpLine') - pl.col('signalDownLine'))).alias('stochastic'),
		])

		longLogic = (pl.col('stochastic') > maxValue)
		shortLogic = (pl.col('stochastic') < minValue)

	elif algo == "bollinger":
		dataFrame = dataFrame.with_columns([
			pl.col('close').rolling_mean(window_size=signalWindow).alias('signalMoving'),
			pl.col('close').rolling_std(window_size=signalWindow).alias('signalSigma'),
		])

		dataFrame = dataFrame.with_columns([
			(pl.col('signalMoving') + pl.col('signalSigma')).alias('signalMovingUpLine'),
			(pl.col('signalMoving') - pl.col('signalSigma')).alias('signalMovingDownLine'),
		])

		longLogic = (pl.col('close') > pl.col('signalMovingDownLine'))
		shortLogic = (pl.col('close') < pl.col('signalMovingUpLine'))

	elif algo == "keltner":
		dataFrame = dataFrame.with_columns([
			pl.col('close').rolling_mean(window_size=signalWindow).alias('signalMoving'),
			(pl.col('high')-pl.col('low')).rolling_std(window_size=signalWindow).alias('ATR'),
		])

		dataFrame = dataFrame.with_columns([
			(pl.col('signalMoving') + pl.col('ATR')).alias('signalMovingUpLine'),
			(pl.col('signalMoving') - pl.col('ATR')).alias('signalMovingDownLine'),
		])

		longLogic = (pl.col('close') > pl.col('signalMovingDownLine'))
		shortLogic = (pl.col('close') < pl.col('signalMovingUpLine'))

	elif algo == "envelopes":
		dataFrame = dataFrame.with_columns(pl.col('close').rolling_mean(window_size=signalWindow).alias('signalMoving'))

		dataFrame = dataFrame.with_columns([
			(pl.col('close') - pl.col('signalMoving')).abs().rolling_mean(window_size=signalWindow).alias('delta'),
		])

		dataFrame = dataFrame.with_columns([
			(pl.col('signalMoving') + pl.col('delta')).alias('signalMovingUpLine'),
			(pl.col('signalMoving') - pl.col('delta')).alias('signalMovingDownLine'),
		])

		longLogic = (pl.col('close') > pl.col('signalMovingDownLine'))
		shortLogic = (pl.col('close') < pl.col('signalMovingUpLine'))

	elif algo == "modeling":
		modelMulti = 0.5

		dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(signalWindow) - 1).alias('signalDiff'))

		dataFrame = dataFrame.with_columns([
			pl.col('signalDiff').abs().alias('secondary'),
			pl.col('volume').rolling_sum(window_size=signalWindow).alias('primary')
		])

		model = simple_correlation(
			secondaryVector=dataFrame['secondary'].to_numpy(),
			primaryVector=dataFrame['primary'].to_numpy(),
			baseWindow=signalWindow
		)

		dataFrame = dataFrame.with_columns(pl.Series('model', model))

		dataFrame = dataFrame.with_columns([
			(pl.lit(modelMulti)*pl.col('model')).alias('pModel'),
			(pl.lit(-modelMulti)*pl.col('model')).alias('nModel'),
		])

		longLogic = (pl.col('signalDiff') > pl.col('pModel'))
		shortLogic = (pl.col('signalDiff') < pl.col('nModel'))

	elif algo == "correlation":
		model = simple_correlation(
			secondaryVector=dataFrame['close'].to_numpy(),
			primaryVector=dataFrame['closeFactor'].to_numpy(),
			baseWindow=signalWindow
		)
		dataFrame = dataFrame.with_columns(pl.Series('model', model))

		longLogic = (pl.col('close') > pl.col('model'))
		shortLogic = (pl.col('close') < pl.col('model'))

	elif algo == "lrcurve":
		lrcurve = simple_linear_regression(
			closeVector=dataFrame['close'].to_numpy(),
			baseWindow=signalWindow
		)
		dataFrame = dataFrame.with_columns(pl.Series('lrcurve', lrcurve))

		longLogic = (pl.col('close') > pl.col('lrcurve'))
		shortLogic = (pl.col('close') < pl.col('lrcurve'))

	elif algo == "lrchannel":
		lrcurve = simple_linear_regression(
			closeVector=dataFrame['close'].to_numpy(),
			baseWindow=signalWindow
		)

		dataFrame = dataFrame.with_columns([
			pl.Series('lrcurve', lrcurve),
			pl.col('close').rolling_std(window_size=signalWindow).alias('sigma'),
		])
		dataFrame = dataFrame.with_columns([
			(pl.col('lrcurve') + pl.col('sigma')).alias('upLine'),
			(pl.col('lrcurve') - pl.col('sigma')).alias('downLine'),
		])

		longLogic = (pl.col('close') > pl.col('upLine'))
		shortLogic = (pl.col('close') < pl.col('downLine'))

	dataFrame = dataFrame.with_columns(
		pl.when(longLogic & (pl.col('close') > pl.col('trendMoving'))).then(pl.lit(2))
		.when(shortLogic & (pl.col('close') < pl.col('trendMoving'))).then(pl.lit(0))
		.otherwise(pl.lit(1))
		.alias('strategy')
	)
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('strategy') == 2).then(pl.lit(-1)).otherwise(pl.lit(1)).alias('long_signal'),
		pl.when(pl.col('strategy') == 0).then(pl.lit(1)).otherwise(pl.lit(-1)).alias('short_signal'),
	])

	#superName = str(output_dir) + f'/moving_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(len(dataFrame)-2500)
	#plt.plot(tempDF['volMulti'], color='blue')
	#plt.plot(tempDF['moving'], color='red')
	#plt.plot(tempDF['trendMoving'], color='blue')
	#plt.savefig(superName)
	#plt.close()

	return dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'leverage'])





