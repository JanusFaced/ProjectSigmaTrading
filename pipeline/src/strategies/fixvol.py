from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import multi_volativity, adaptive_moving
from convertorTF import convertorTimeFrame
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

	numberTimeframe = convertorTimeFrame(timeFrame)
	targetVolativity = 2.0
	targetTimeframe = 240
	
	signalWindow, filterWindow = 20, 200 #20, 200
	depthSwitch = 4
	maxMulti = 2**depthSwitch
	minMulti = 1

	leverage = 3
	dataFrame = dataFrame.with_columns(pl.lit(leverage).alias('leverage'))

	volMulti = multi_volativity(
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		baseVolativity=targetVolativity*(numberTimeframe/targetTimeframe)**(0.5),
		baseWindow=filterWindow,
		depth=depthSwitch
	)
	dataFrame = dataFrame.with_columns(pl.Series('volMulti', volMulti))

	upLineMoving, moving, downLineMoving, movingDiff = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		multiple=1.0,
		baseLineMode="MA",
		depth=depthSwitch
	)
	dataFrame = dataFrame.with_columns([
		pl.Series('signalUpLineMoving', upLineMoving),
		pl.Series('signalMoving', moving),
		pl.Series('signalDownLineMoving', downLineMoving),
		pl.Series('signalMovingDiff', movingDiff),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('signalMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('signalMoving')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(0))
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

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'leverage'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
