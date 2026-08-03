from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import multi_volativity, adaptive_correlation
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
	volativityConvertor = {
		"BTC": 4.0,
		"ETH": 7.0,
		"BNB": 5.0,
		"XRP": 7.0,
		"SOL": 7.0,
		"TRX": 3.0,
		"ADA": 7.0,
		"LINK": 7.0,
		"HYPE": 10.0,
		"RE": 12.0,
		"BOT": 12.0,
	}
	baseVolativity = volativityConvertor[symbol]
	signalWindow, filterWindow = 20, 200 #20, 200
	angle = 0.85
	depthSwitch = 4
	maxMulti = 2**depthSwitch
	minMulti = 1

	volMulti = multi_volativity(
		highVector=dataFrame['high'].to_numpy(),
		lowVector=dataFrame['low'].to_numpy(),
		baseVolativity=baseVolativity*(numberTimeFrame/1440)**(angle),
		baseWindow=filterWindow,
		depth=depthSwitch
	)
	dataFrame = dataFrame.with_columns(pl.Series('volMulti', volMulti))

	model = adaptive_correlation(
		secondaryVector=dataFrame['close'].to_numpy(),
		primaryVector=dataFrame['closeFactor'].to_numpy(),
		volMulti=dataFrame['volMulti'].to_numpy(),
		baseWindow=signalWindow,
		depth=depthSwitch
	)
	dataFrame = dataFrame.with_columns([
		pl.Series('model', model),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('model')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('model')) &
			(maxMulti > pl.col('volMulti')) & (pl.col('volMulti') > minMulti)
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

