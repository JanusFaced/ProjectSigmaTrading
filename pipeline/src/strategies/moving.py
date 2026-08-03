from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import multi_volativity, adaptive_moving, adaptive_adx
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

	numberTimeFrame = convertorTimeFrame(timeFrame)

	signalWindow, directWindow, filterWindow = 20, 100, 200 #20, 100, 200
	baseVolativity = 10.0*numberTimeFrame/1440 #10.0
	depthSwitch = 4 #4

	volMulti = multi_volativity(
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		baseVolativity=baseVolativity,
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

	pDMI, nDMI, direct, directDiff = adaptive_adx(
		openVector=dataFrame['open'].to_numpy(),
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=directWindow,
		depth=depthSwitch
	)

	trendUpLineMoving, trendMoving, trendDownLineMoving, trendMovingDiff = adaptive_moving(
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=filterWindow,
		multiple=1.0,
		baseLineMode="MA",
		depth=depthSwitch
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('upLineMoving', upLineMoving),
		pl.Series('moving', moving),
		pl.Series('downLineMoving', downLineMoving),
		pl.Series('movingDiff', movingDiff),
		pl.Series('pDMI', pDMI),
		pl.Series('nDMI', nDMI),
		pl.Series('direct', direct),
		pl.Series('directDiff', directDiff),
		pl.Series('trendUpLineMoving', trendUpLineMoving),
		pl.Series('trendMoving', trendMoving),
		pl.Series('trendDownLineMoving', trendDownLineMoving),
		pl.Series('trendMovingDiff', trendMovingDiff),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('moving')) &
			(pl.col('close') > pl.col('trendMoving')) & (pl.col('trendMovingDiff') > 0) &
			(pl.col('directDiff') > 0) &
			(pl.col('volMulti') < 15) &
			(pl.col('volMulti') > 1)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('moving')) &
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

	#superName = str(output_dir) + f'/moving_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(2500)
	#plt.plot(tempDF['volMulti'], color='black')
	#plt.plot(tempDF['moving'], color='red')
	#plt.plot(tempDF['trendMoving'], color='blue')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
