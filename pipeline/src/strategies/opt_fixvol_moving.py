from typing import Any
import matplotlib.pyplot as plt
import polars as pl
import os
from custom_ta import adaptive_moving
from convertorTF import convertorTimeFrame
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

	train_size, test_size = 10000, 3000
	quantSlippage = 3000
	parametrs = {
		"targetVolativity": {"min": 100, "max": 1000, "split": 10},
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
	
	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	targetVolativity = 0.01*params['targetVolativity']
	
	numberTimeframe = convertorTimeFrame(timeFrame)
	targetTimeframe = 240
	
	signalWindow, filterWindow = 20, 200 #20, 200
	depthSwitch = 4
	maxMulti = 2**depthSwitch
	minMulti = 1

	leverage = 1
	dataFrame = dataFrame.with_columns(pl.lit(leverage).alias('leverage'))

	timeframeVolativity=targetVolativity*(numberTimeframe/targetTimeframe)**(0.5)
	dataFrame = dataFrame.with_columns([
		(100*(pl.col('high')/pl.col('low') - 1)).rolling_mean(window_size=filterWindow).alias('ATR')
	])
	dataFrame = dataFrame.with_columns([
		(pl.lit(timeframeVolativity)/pl.col('ATR')).clip(0.1, 16).alias('volMulti')
	])

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

	#superName = str(output_dir) + f'/{targetVolativity}_optFixvolMoving_{nameExchange}_{symbol}_{type}_{timeFrame}.png'
	#tempDF = dataFrame.tail(1000)
	#plt.plot(tempDF['volMulti'], color='blue')
	#plt.savefig(superName)
	#plt.close()

	return dataFrame





