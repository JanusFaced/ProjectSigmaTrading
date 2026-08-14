from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import adaptive_moving
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

	signalWindow, trendWindow, currentVolativityWindow, targetVolativityWindow = 20, 200, 200, 2000
	depthSwitch = 4
	maxMulti, minMulti = 2**depthSwitch, 1.0
	leverage = 1
	multiMaxLoss = 1
	multiMaxProfit = 100

	dataFrame = dataFrame.with_columns(pl.lit(leverage).alias('leverage'))

	dataFrame = dataFrame.with_columns([
		(pl.col('high')/pl.col('low')-1).alias('TR'),
	])
	dataFrame = dataFrame.with_columns([
		pl.col('TR').rolling_mean(window_size=currentVolativityWindow).alias('ATR'),
		pl.col('TR').rolling_mean(window_size=targetVolativityWindow).alias('slowATR'),
	])
	dataFrame = dataFrame.with_columns([
		(pl.col('slowATR')/pl.col('ATR')).clip(0.1, 16).alias('volMulti'),
	])

	upLine, signalMoving, downLine, movingDiff = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		multiple=1.0,
		baseLineMode="LR",
		depth=depthSwitch
	)

	upLine, trendMoving, downLine, movingDiff = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=trendWindow,
		multiple=1.0,
		baseLineMode="MA",
		depth=depthSwitch
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('signalMoving', signalMoving),
		pl.Series('trendMoving', trendMoving),
	])

	dataFrame = dataFrame.with_columns([
		(pl.lit(-multiMaxLoss)*pl.col('ATR')).alias('maxLoss'),
		(pl.lit(multiMaxProfit)*pl.col('ATR')).alias('maxProfit'),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('signalMoving')) & (pl.col('signalMoving') > pl.col('close').shift(1)) &
			(pl.col('close') > pl.col('trendMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(-1))
		.when(
			(pl.col('close') < pl.col('signalMoving')) & (pl.col('signalMoving') < pl.col('close').shift(1)) &
			(pl.col('close') > pl.col('trendMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('long_signal'),

		pl.when(
			(pl.col('close') > pl.col('signalMoving')) & (pl.col('signalMoving') > pl.col('close').shift(1)) &
			(pl.col('close') < pl.col('trendMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(-1))
		.when(
			(pl.col('close') < pl.col('signalMoving')) & (pl.col('signalMoving') < pl.col('close').shift(1)) &
			(pl.col('close') < pl.col('trendMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(1))
		.otherwise(pl.lit(0))
		.alias('short_signal'),
	)

	#superName = str(output_dir) + f'/moving_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(len(dataFrame)-2500)
	#plt.plot(tempDF['volMulti'], color='blue')
	#plt.plot(tempDF['moving'], color='red')
	#plt.plot(tempDF['trendMoving'], color='blue')
	#plt.savefig(superName)
	#plt.close()

	validList = [
		'datetime',
		'open', 'high', 'low', 'close', 'volume',
		'long_signal', 'short_signal', 'leverage',
		'maxLoss', 'maxProfit',
	]

	dataFrame = dataFrame.select(validList)
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
