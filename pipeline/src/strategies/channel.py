from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import adaptive_lr_channel, adaptive_moving, adaptive_adx
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

	signalWindow, directWindow, filterWindow = 20, 100, 200 #20, 200
	baseVolativity = 1.000 #1.000

	dataFrame = dataFrame.with_columns((100*(pl.col('high')/pl.col('low') - 1)).alias('trueRange'))
	dataFrame = dataFrame.with_columns(pl.col('trueRange').rolling_mean(window_size=filterWindow).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseVolativity)/pl.col('volativity')).alias('volMulti'))
	dataFrame = dataFrame.with_columns([
		(pl.col('volMulti')*signalWindow).fill_null(signalWindow).cast(pl.Int64).clip(2, None).alias('signalWindow'),
		(pl.col('volMulti')*directWindow).fill_null(directWindow).cast(pl.Int64).clip(2, None).alias('directWindow'),
		(pl.col('volMulti')*filterWindow).fill_null(filterWindow).cast(pl.Int64).clip(2, None).alias('filterWindow'),
	])

	signalUp, signalCurve, signalDown = adaptive_lr_channel(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)

	pDMI, nDMI, direct = adaptive_adx(
		openVector=dataFrame['open'].to_numpy(),
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['directWindow'].to_numpy()
	)

	trendMoving = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['filterWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('signalUp', signalUp),
		pl.Series('signalCurve', signalCurve),
		pl.Series('signalDown', signalDown),
		pl.Series('direct', direct),
		pl.Series('trendMoving', trendMoving),
	])

	dataFrame = dataFrame.with_columns([
		(pl.col('direct')/pl.col('direct').shift(1) - 1).alias('directDiff'),
		(pl.col('trendMoving')/pl.col('trendMoving').shift(1) - 1).alias('trendMovingDiff'),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('signalDown')) &
			(pl.col('close') > pl.col('trendMoving')) & (pl.col('trendMovingDiff') > 0) &
			(pl.col('directDiff') > 0) &
			(pl.col('volMulti') < 15) &
			(pl.col('volMulti') > 1)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('signalUp')) &
			(pl.col('close') < pl.col('trendMoving')) & (pl.col('trendMovingDiff') < 0) &
			(pl.col('directDiff') > 0) &
			(pl.col('volMulti') < 15) &
			(pl.col('volMulti') > 1)
		).then(pl.lit(0))
		.otherwise(pl.lit(1))
		.alias('strategy')
	)
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('strategy') == 2).then(pl.lit(-1)).otherwise(pl.lit(1)).alias('long_signal'),
		pl.when(pl.col('strategy') == 0).then(pl.lit(1)).otherwise(pl.lit(-1)).alias('short_signal'),
	])

	#superName = str(output_dir) + f'/channel_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1440)
	#plt.plot(tempDF['close'], color='black')
	#plt.plot(tempDF['signalUp'], color='green')
	#plt.plot(tempDF['signalCurve'], color='orange')
	#plt.plot(tempDF['signalDown'], color='red')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
