from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from walk_forward_simulator import walkForward
from pathlib import Path
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	db = get_duckdb()
	dataFrame = db.execute("SELECT * FROM temp_analyst").pl()
	db.execute("DROP TABLE IF EXISTS temp_analyst")

	train_size, test_size = 1000, 300
	quantSlippage = 2000
	parametrs = {
		"signalWindow": {"min": 20, "max": 200, "split": 5},
	}

	dataFrame = walkForward(
		algorithm=algorithm,
		train_size=train_size,
		test_size=test_size,
		inputMessage=inputMessage,
		originalDataFrame=dataFrame,
		parametrs=parametrs,
		quantSlippage=quantSlippage
	)

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal', 'leverage'])
	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")

def algorithm(
		dataFrame: pl.DataFrame,
		inputMessage: dict,
		params: dict
	) -> pl.DataFrame:

	signalWindow = params['signalWindow']
	trendWindow = 10*signalWindow
	
	leverage = 1

	dataFrame = dataFrame.with_columns([
		pl.lit(leverage).alias('leverage'),
		pl.col('close').rolling_mean(window_size=signalWindow).alias('signalMoving'),
		pl.col('close').rolling_std(window_size=signalWindow).alias('signalSigma'),
		pl.col('close').rolling_mean(window_size=trendWindow).alias('trendMoving'),
	])
	dataFrame = dataFrame.with_columns([
		(pl.col('signalMoving') + pl.col('signalSigma')).alias('signalMovingUpLine'),
		(pl.col('signalMoving') - pl.col('signalSigma')).alias('signalMovingDownLine'),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('close') > pl.col('signalMovingDownLine')) &
			(pl.col('close') > pl.col('trendMoving'))
		).then(pl.lit(2))
		.when(
			(pl.col('close') < pl.col('signalMovingUpLine')) &
			(pl.col('close') < pl.col('trendMoving'))
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

	return dataFrame





