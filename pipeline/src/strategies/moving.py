from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from convertorTF import convertorTimeFrame
from custom_ta import adaptive_moving, adaptive_roc
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

	volativityWindow, directionWindow, signalWindow, trendWindow = 200, 200, 20, 200
	maxVolMulti, minVolMulti = 15, 1
	maxDirMulti = 15
	
	base1m = 0.000075
	convertA = 1440
	convertB = 0.06
	convertC = convertorTimeFrame(timeFrame)
	baseValue = base1m*( convertB*(convertA - convertC) + convertC )

	if convertC == 1440:
		dataFrame = dataFrame.with_columns([
			(pl.lit(signalWindow).alias('signalWindow')),
			(pl.lit(trendWindow).alias('trendWindow')),
		])

	else:
		dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).abs().alias('diff_abs'))
		dataFrame = dataFrame.with_columns(pl.col('diff_abs').rolling_mean(window_size=volativityWindow).alias('volativity'))
		dataFrame = dataFrame.with_columns((pl.lit(baseValue)/pl.col('volativity')).alias('volMulti'))
		dataFrame = dataFrame.with_columns([
			(pl.col('volMulti')*signalWindow).fill_null(signalWindow).cast(pl.Int64).clip(2, None).alias('signalWindow'),
			(pl.col('volMulti')*trendWindow).fill_null(trendWindow).cast(pl.Int64).clip(2, None).alias('trendWindow'),
		])

		if convertC <= 60:
			dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).alias('diff'))
			dataFrame = dataFrame.with_columns(pl.col('diff').rolling_mean(window_size=directionWindow).abs().alias('direction'))
			dataFrame = dataFrame.with_columns((pl.lit(baseValue)/pl.col('direction')).alias('dirMulti'))

	moving = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)

	trend = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['trendWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('moving', moving),
		pl.Series('trend', trend),
	])

	if convertC == 1440:
		dataFrame = dataFrame.with_columns(
			pl.when(
				(pl.col('close') > pl.col('moving')) &
				(pl.col('trend') > 0)
			).then(pl.lit(2))
			.when(
				(pl.col('close') < pl.col('moving')) &
				(pl.col('trend') < 0)
			).then(pl.lit(0))
			.otherwise(pl.lit(1))
			.alias('strategy')
		)

	elif 60 < convertC < 1440:
		dataFrame = dataFrame.with_columns(
			pl.when(
				(pl.col('close') > pl.col('moving')) &
				(pl.col('trend') > 0) &
				(pl.col('volMulti') < maxVolMulti) &
				(pl.col('volMulti') > minVolMulti)
			).then(pl.lit(2))
			.when(
				(pl.col('close') < pl.col('moving')) &
				(pl.col('trend') < 0) &
				(pl.col('volMulti') < maxVolMulti) &
				(pl.col('volMulti') > minVolMulti)
			).then(pl.lit(0))
			.otherwise(pl.lit(1))
			.alias('strategy')
		)

	else:
		dataFrame = dataFrame.with_columns(
			pl.when(
				(pl.col('close') > pl.col('moving')) &
				(pl.col('trend') > 0) &
				(pl.col('volMulti') < maxVolMulti) &
				(pl.col('volMulti') > minVolMulti) &
				(pl.col('dirMulti') < maxDirMulti)
			).then(pl.lit(2))
			.when(
				(pl.col('close') < pl.col('moving')) &
				(pl.col('trend') < 0) &
				(pl.col('volMulti') < maxVolMulti) &
				(pl.col('volMulti') > minVolMulti) &
				(pl.col('dirMulti') < maxDirMulti)
			).then(pl.lit(0))
			.otherwise(pl.lit(1))
			.alias('strategy')
		)
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('strategy') == 2).then(pl.lit(-1)).otherwise(pl.lit(1)).alias('long_signal'),
		pl.when(pl.col('strategy') == 0).then(pl.lit(1)).otherwise(pl.lit(-1)).alias('short_signal'),
	])

	#superName = str(output_dir) + f'/moving_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1440)
	#tempDF = tempDF.with_columns(
	#	pl.when( (pl.col('dirMulti') > pl.lit(maxDirMulti)) ).then( pl.lit(maxDirMulti) )
	#	.otherwise(pl.col('dirMulti'))
	#	.alias('dirMulti')
	#)
	#tempDF = tempDF.with_columns([pl.lit(maxDirMulti).alias('maxDirMulti')])
	#plt.plot(tempDF['close'], color='black')
	#plt.plot(tempDF['moving'], color='red')
	#plt.plot(tempDF['volMulti'], color='orange')
	#plt.plot(tempDF['maxDirMulti'], color='red')
	#plt.plot(tempDF['dirMulti'], color='purple')
	#plt.plot(tempDF['volativity'], color='black')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
