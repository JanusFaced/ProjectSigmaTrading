from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from convertorTF import convertorTimeFrame
from custom_ta import adaptive_modeling_correlation, adaptive_moving
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

	convertTimeFrame = convertorTimeFrame(timeFrame)

	signalWindow, filterWindow = 20, 200 #20, 200
	
	baseVolativity = 0.000075 #0.000075
	convertAngle = 0.06 #0.06
	baseValueVolativity = baseVolativity*( convertAngle*(1440 - convertTimeFrame) + convertTimeFrame )

	dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).abs().alias('diff_abs'))
	dataFrame = dataFrame.with_columns(pl.col('diff_abs').rolling_mean(window_size=filterWindow).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseValueVolativity)/pl.col('volativity')).alias('volMulti'))
	dataFrame = dataFrame.with_columns([
		(pl.col('volMulti')*signalWindow).fill_null(signalWindow).cast(pl.Int64).clip(2, None).alias('signalWindow'),
		(pl.col('volMulti')*filterWindow).fill_null(filterWindow).cast(pl.Int64).clip(2, None).alias('filterWindow'),
	])

	model = adaptive_modeling_correlation(
		secondaryVector=dataFrame['close'].to_numpy(),
		primaryVector=dataFrame['closeFactor'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)

	trendMoving = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['filterWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('model', model),
		pl.Series('trendMoving', trendMoving),
	])

	dataFrame = dataFrame.with_columns([
		(pl.col('model')/pl.col('model').shift(1) - 1).abs().alias('modelDiff'),
		(pl.col('trendMoving')/pl.col('trendMoving').shift(1) - 1).abs().alias('trendMovingDiff'),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('model')) & (pl.col('modelDiff') > 0) &
			(pl.col('close') > pl.col('trendMoving')) & (pl.col('trendMovingDiff') > 0) &
			(pl.col('volMulti') < 15) &
			(pl.col('volMulti') > 1)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('model')) & (pl.col('modelDiff') < 0) &
			(pl.col('close') < pl.col('trendMoving')) & (pl.col('trendMovingDiff') < 0) &
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

	#superName = str(output_dir) + f'/correlation_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1440)
	#plt.plot(tempDF['close'], color='black')
	#plt.plot(tempDF['model'], color='purple')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

