from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import adaptive_adx, adaptive_moving
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

	signalWindow, directWindow, filterWindow = 20, 100, 200 #20, 100, 200
	baseVolativity = 1.0 #1.0
	depthSwitch = 4 #4

	dataFrame = dataFrame.with_columns((100*(pl.col('high')/pl.col('low') - 1)).alias('trueRange'))
	dataFrame = dataFrame.with_columns(pl.col('trueRange').rolling_mean(window_size=filterWindow).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseVolativity)/pl.col('volativity')).fill_null(1.0).alias('volMulti'))

	signalPos, signalNeg, signalDirect, signalDirectDiff = adaptive_adx(
		openVector=dataFrame['open'].to_numpy(),
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
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
		pl.Series('signalPos', signalPos),
		pl.Series('signalNeg', signalNeg),
		pl.Series('direct', direct),
		pl.Series('directDiff', directDiff),
		pl.Series('trendMoving', trendMoving),
		pl.Series('trendMovingDiff', trendMovingDiff),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('signalPos') > pl.col('signalNeg')) &
			(pl.col('close') > pl.col('trendMoving')) & (pl.col('trendMovingDiff') > 0) &
			(pl.col('directDiff') > 0) &
			(pl.col('volMulti') < 15) &
			(pl.col('volMulti') > 1)
		).then(pl.lit(2))
		.when(
			(pl.col('signalPos') < pl.col('signalNeg')) &
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

	#superName = str(output_dir) + f'/trend_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1440)
	#plt.plot(tempDF['pDMI'], color='green')
	#plt.plot(tempDF['nDMI'], color='red')
	#plt.plot(tempDF['ADX'], color='blue')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
