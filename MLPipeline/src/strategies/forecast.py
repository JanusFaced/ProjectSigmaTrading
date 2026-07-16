from typing import Any, TypedDict
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import os
from convertorTF import convertorTimeFrame
from pathlib import Path
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	db = get_duckdb()
	dataFrame = db.execute("SELECT * FROM temp_analyst ORDER BY datetime").pl()

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']

	volativityWindow = 200
	signalWindow = 20
	trendWindow = 200
	maxMulti = 15
	minMulti = 1
	baseVolativity1m = 0.0004
	baseVolativity = baseVolativity1m*convertorTimeFrame(timeFrame)

	dataFrame = dataFrame.with_columns((pl.col('close')/pl.col('close').shift(1) - 1).abs().alias('diff'))
	dataFrame = dataFrame.with_columns(pl.col('diff').rolling_mean(window_size=volativityWindow).alias('volativity'))
	dataFrame = dataFrame.with_columns((pl.lit(baseVolativity)/pl.col('volativity')).alias('window'))

	dataFrame = dataFrame.with_columns([
		(pl.col('window')*signalWindow).fill_null(signalWindow).cast(pl.Int64).clip(2, None).alias('signalWindow'),
		(pl.col('window')*trendWindow).fill_null(trendWindow).cast(pl.Int64).clip(2, None).alias('trendWindow'),
	])

	model = adaptive_lr_forecast(
		diffVector=dataFrame['diff'].to_numpy(),
		windowVector=dataFrame['signalWindow'].to_numpy()
	)
	trend = adaptive_roc(
		closeVector=dataFrame['close'].to_numpy(),
		windowVector=dataFrame['trendWindow'].to_numpy()
	)

	dataFrame = dataFrame.with_columns([
		pl.Series('model', model),
		pl.Series('trend', trend),
	])

	dataFrame = dataFrame.with_columns(
		pl.when(
			(pl.col('diff') > pl.col('model')) &
			(pl.col('trend') > 0) &
			(pl.col('window') < maxMulti) &
			(pl.col('window') > minMulti)
		).then(pl.lit(2))
		.when(
			(pl.col('diff') < pl.col('model')) &
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

	dataFrame = dataFrame.select(['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal'])

	db.execute("CREATE OR REPLACE TEMP TABLE temp_trading AS SELECT * FROM dataFrame")
	logger.info(f"Сохранено в temp_trading!")
	
	db.execute("DROP TABLE IF EXISTS temp_analyst")
	logger.info("temp_analyst удалена!")

@njit
def adaptive_lr_forecast(
		diffVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> npt.NDArray[np.float64]:
	
	lenth = len(diffVector)
	modelLineVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i
		window = windowVector[i]
		cutWindow = diffVector[real_i-window:real_i]
		modelLineVector[i] = linearRegression(cutWindow)

	return modelLineVector

@njit
def linearRegression(cutWindow: npt.NDArray[np.float64]) -> np.float64:
	lenth = len(cutWindow)
	if lenth < 2:
		lastValue = cutWindow[0] if lenth == 1 else 0.0

	else:
		sum_x = lenth*(lenth + 1) / 2
		sum_x2 = lenth*(lenth + 1) * (2*lenth + 1)/6
		
		sum_y = 0.0
		sum_xy = 0.0
		for i in range(lenth):
			xi = i + 1
			sum_y += cutWindow[i]
			sum_xy += xi*cutWindow[i]
		
		denominator = lenth*sum_x2 - sum_x*sum_x
		if denominator == 0:
			lastValue = cutWindow[-1]

		else:
			parametr_b = (lenth * sum_xy - sum_x * sum_y) / denominator
			parametr_a = (sum_y - parametr_b * sum_x) / lenth
			lastValue = parametr_a + parametr_b*lenth
	
	return lastValue

@njit
def adaptive_roc(closeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)

	rocVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		rocVector[i] = cutClose[-1]/cutClose[0] - 1

	return rocVector