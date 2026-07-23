from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from convertorTF import convertorTimeFrame
from custom_ta import adaptive_lr_channel, adaptive_roc
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

	upLine, baseLine, downLine = adaptive_lr_channel(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)
	trend = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['trendWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('upLine', upLine),
		pl.Series('baseLine', baseLine),
		pl.Series('downLine', downLine),
		pl.Series('trend', trend),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('downLine')) &
			(pl.col('trend') > 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('upLine')) &
			(pl.col('trend') < 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
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
	#plt.plot(tempDF['upLine'], color='green')
	#plt.plot(tempDF['baseLine'], color='orange')
	#plt.plot(tempDF['downLine'], color='red')
	#plt.plot(tempDF['window'], color='black')
	#plt.savefig(superName)
	#plt.close()

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
