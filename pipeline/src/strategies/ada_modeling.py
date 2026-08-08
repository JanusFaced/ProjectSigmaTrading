from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import os
from custom_ta import adaptive_roc, adaptive_volume, adaptive_correlation
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

	signalWindow, trendWindow, currentVolativityWindow, targetVolativityWindow = 20, 200, 200, 2000
	depthSwitch = 4
	maxMulti, minMulti = 2**depthSwitch, 1.0
	leverage = 1
	multiModel = 0.5

	dataFrame = dataFrame.with_columns(pl.lit(leverage).alias('leverage'))

	dataFrame = dataFrame.with_columns([
		(pl.lit(100)*(pl.col('high')/pl.col('low')-1)).alias('TR'),
	])
	dataFrame = dataFrame.with_columns([
		pl.col('TR').rolling_mean(window_size=currentVolativityWindow).alias('fastATR'),
		pl.col('TR').rolling_mean(window_size=targetVolativityWindow).alias('slowATR'),
	])
	dataFrame = dataFrame.with_columns([
		(pl.col('slowATR')/pl.col('fastATR')).clip(0.1, 16).alias('volMulti'),
	])

	signalDiff = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		depth=depthSwitch
	)
	primary = adaptive_volume(
		volumeVector=dataFrame['volume'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		depth=depthSwitch
	)
	model = adaptive_correlation(
		secondaryVector=abs(signalDiff),
		primaryVector=primary,
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		depth=depthSwitch
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('signalDiff', signalDiff),
		pl.Series('model', model),
	])

	dataFrame = dataFrame.with_columns([
		(pl.lit(multiModel)*pl.col('model')).alias('pModel'),
		(pl.lit(-multiModel)*pl.col('model')).alias('nModel'),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('signalDiff') > pl.col('pModel')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(2))
		.when(
			(pl.col('signalDiff') < pl.col('nModel')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(0))
		.otherwise(pl.lit(1))
		.alias('strategy')
	)
	
	dataFrame = dataFrame.with_columns([
		pl.when(pl.col('strategy') == 2).then(pl.lit(-1)).otherwise(pl.lit(1)).alias('long_signal'),
		pl.when(pl.col('strategy') == 0).then(pl.lit(1)).otherwise(pl.lit(-1)).alias('short_signal'),
	])

	#superName = str(output_dir) + f'/modeling_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1440)
	#plt.plot(tempDF['signalDiff'], color='black')
	#plt.plot(tempDF['nModel'], color='red')
	#plt.plot(tempDF['pModel'], color='green')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'leverage'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
