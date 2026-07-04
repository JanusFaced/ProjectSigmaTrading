from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
import os
import sys
from convertorTF import convertorTimeFrame
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> pd.DataFrame:

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

	dataFrame['diff'] = np.abs(dataFrame['close']/dataFrame['close'].shift(1) - 1)
	dataFrame['volativity'] = dataFrame['diff'].rolling(window=volativityWindow).mean()
	dataFrame['window'] = baseVolativity/dataFrame['volativity']

	dataFrame['signalWindow'] = (signalWindow*dataFrame['window']).fillna(signalWindow).astype(np.int64).clip(lower=2)
	dataFrame['trendWindow'] = (trendWindow*dataFrame['window']).fillna(trendWindow).astype(np.int64).clip(lower=2)

	dataFrame['model'] = adaptive_lr_forecast(diffVector=dataFrame['diff'].values, windowVector=dataFrame['signalWindow'].values)
	dataFrame['trend'] = adaptive_roc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trendWindow'].values)

	dataFrame['strategy'] = np.select(
		[
			(dataFrame['diff'] > dataFrame['model']) & (dataFrame['trend'] > 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti),
			(dataFrame['diff'] < dataFrame['model']) & (dataFrame['trend'] < 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti)
		],
		[2, 0], default=1
	)

	dataFrame['long_signal'] = np.select([dataFrame['strategy'] == 2], [-1], default=1)
	dataFrame['short_signal'] = np.select([dataFrame['strategy'] == 0], [1], default=-1)

	#testDF = dataFrame.tail(50)
	#superName = f"lr_channel_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['diff'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="orange")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

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