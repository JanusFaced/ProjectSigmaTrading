from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from convertorTF import convertorTimeFrame
from custom_ta import adaptive_price_channel, adaptive_roc
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

	volativityWindow, signalWindow, trendWindow = 200, 20, 200
	maxMulti, minMulti = 15, 1
	baseVolativity1m = 0.0004
	baseVolativity = baseVolativity1m*convertorTimeFrame(timeFrame)

	dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).abs().alias('diff'))
	dataFrame = dataFrame.with_columns(pl.col('diff').rolling_mean(window_size=volativityWindow).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseVolativity)/pl.col('volativity')).alias('window'))

	dataFrame = dataFrame.with_columns([
		(pl.col('window')*signalWindow).fill_null(signalWindow).cast(pl.Int64).clip(2, None).alias('signalWindow'),
		(pl.col('window')*trendWindow).fill_null(trendWindow).cast(pl.Int64).clip(2, None).alias('trendWindow'),
	])

	dataFrame = dataFrame.with_columns([
		(pl.col('close') - pl.col('open')).alias('coloreBody'),
		(pl.col('close') - pl.col('open')).abs().alias('sizeBody'),
	])
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('coloreBody') > 0)
		.then(pl.col('high') - pl.col('close'))
		.otherwise(pl.col('high') - pl.col('open'))
		.alias('sizeUpWick'),
		
		pl.when(pl.col('coloreBody') > 0)
		.then(pl.col('open') - pl.col('low'))
		.otherwise(pl.col('close') - pl.col('low'))
		.alias('sizeDownWick'),
	])
	
	dataFrame = dataFrame.with_columns([
		pl.col('coloreBody').shift(1).alias('coloreBody1'),
		pl.col('sizeBody').shift(1).alias('sizeBody1'),
		pl.col('coloreBody').shift(2).alias('coloreBody2'),
		pl.col('sizeBody').shift(2).alias('sizeBody2'),
		pl.col('high').shift(1).alias('high1'),
		pl.col('high').shift(2).alias('high2'),
		pl.col('high').shift(3).alias('high3'),
		pl.col('high').shift(4).alias('high4'),
		pl.col('low').shift(1).alias('low1'),
		pl.col('low').shift(2).alias('low2'),
		pl.col('low').shift(3).alias('low3'),
		pl.col('low').shift(4).alias('low4'),
	])
	
	dataFrame = dataFrame.with_columns([
		pl.when(
			(pl.col('coloreBody') > 0) &
			(pl.col('sizeDownWick') > pl.col('sizeBody')) &
			(pl.col('sizeBody') > pl.col('sizeUpWick'))
		).then(pl.lit(-1))
		.when(
			(pl.col('coloreBody') < 0) &
			(pl.col('sizeDownWick') < pl.col('sizeBody')) &
			(pl.col('sizeBody') < pl.col('sizeUpWick'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('pinbar'),
		
		pl.when(
			(pl.col('sizeBody') > pl.col('sizeBody1')) &
			(pl.col('coloreBody') > 0) &
			(pl.col('coloreBody1') < 0)
		).then(pl.lit(-1))
		.when(
			(pl.col('sizeBody') > pl.col('sizeBody1')) &
			(pl.col('coloreBody') < 0) &
			(pl.col('coloreBody1') > 0)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('engulfing'),
		
		pl.when(
			(pl.col('sizeBody') > pl.col('sizeBody2')) &
			(pl.col('sizeBody2') > pl.col('sizeBody1')) &
			(pl.col('coloreBody') > 0) &
			(pl.col('coloreBody2') < 0)
		).then(pl.lit(-1))
		.when(
			(pl.col('sizeBody') > pl.col('sizeBody2')) &
			(pl.col('sizeBody2') > pl.col('sizeBody1')) &
			(pl.col('coloreBody') < 0) &
			(pl.col('coloreBody2') > 0)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('star'),
		
		pl.when(
			(pl.col('low2') < pl.col('low')) &
			(pl.col('low2') < pl.col('low1')) &
			(pl.col('low2') < pl.col('low3')) &
			(pl.col('low2') < pl.col('low4'))
		).then(pl.lit(-1))
		.when(
			(pl.col('high2') > pl.col('high')) &
			(pl.col('high2') > pl.col('high1')) &
			(pl.col('high2') > pl.col('high3')) &
			(pl.col('high2') > pl.col('high4'))
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('fractal'),
		
		pl.when(
			(pl.col('coloreBody') > 0) &
			(pl.col('coloreBody1') > 0) &
			(pl.col('coloreBody2') > 0)
		).then(pl.lit(-1))
		.when(
			(pl.col('coloreBody') < 0) &
			(pl.col('coloreBody1') < 0) &
			(pl.col('coloreBody2') < 0)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('soldiers'),
	])
	
	dataFrame = dataFrame.with_columns([
		pl.when(
			(pl.col('pinbar') == -1) |
			(pl.col('engulfing') == -1) |
			(pl.col('star') == -1) |
			(pl.col('fractal') == -1) |
			(pl.col('soldiers') == -1)
		).then(pl.lit(-1))
		.otherwise(pl.lit(0))
		.alias('long_pattern'),
		
		pl.when(
			(pl.col('pinbar') == 1) |
			(pl.col('engulfing') == 1) |
			(pl.col('star') == 1) |
			(pl.col('fractal') == 1) |
			(pl.col('soldiers') == 1)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_pattern'),
	])
	
	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('long_pattern') == -1) &
			(pl.col('short_pattern') == 0)
		).then(pl.lit(-1))
		.when(
			(pl.col('short_pattern') == 1) &
			(pl.col('long_pattern') == 0)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('pattern')
	)

	upLine, meanLine, downLine = adaptive_price_channel(
		openVector=dataFrame['open'].to_numpy(),
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)
	
	trend = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['trendWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('upLine', upLine),
		pl.Series('meanLine', meanLine),
		pl.Series('downLine', downLine),
		pl.Series('trend', trend),
	])

	dataFrame = dataFrame.with_columns([
		pl.col('upLine').shift(1).alias('upLineOld'),
		pl.col('downLine').shift(1).alias('downLineOld'),
	])

	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('pattern') == -1)
		.then(pl.lit(-1))
		.when(pl.col('close') < pl.col('downLineOld'))
		.then(pl.lit(1))
		.otherwise(pl.lit(1))
		.alias('long_signal_temp'),

		pl.when(pl.col('pattern') == 1)
		.then(pl.lit(1))
		.when(pl.col('close') > pl.col('upLineOld'))
		.then(pl.lit(-1))
		.otherwise(pl.lit(-1))
		.alias('short_signal_temp'),
	])

	dataFrame = dataFrame.with_columns([
		pl.when(
			(pl.col('trend') > 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.col('long_signal_temp'))
		.otherwise(pl.lit(1))
		.alias('long_signal'),
		
		pl.when(
			(pl.col('trend') < 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.col('short_signal_temp'))
		.otherwise(pl.lit(-1))
		.alias('short_signal'),
	])

	#superName = str(output_dir) + f'/pattern_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(100)
	#plt.plot(tempDF['close'], color='black')
	#plt.plot(tempDF['close']*(1 + 0.01*tempDF['pattern']), color='purple')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
