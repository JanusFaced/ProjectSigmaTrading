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

	strategy = inputMessage['strategy']
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

	dataFrame['original'] = dataFrame['close']
	dataFrame['primary'] = dataFrame['closeFactor']

	dataFrame['model'] = adaptive_modeling(
		secondaryVector=dataFrame['original'].values,
		primaryVector=dataFrame['primary'].values,
		windowVector=dataFrame['signalWindow'].values
	)
	
	dataFrame['trend'] = adaptiveRoc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trendWindow'].values)

	dataFrame['strategy'] = np.select(
		[
			(dataFrame['original'] > dataFrame['model']) & (dataFrame['trend'] > 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti),
			(dataFrame['original'] < dataFrame['model']) & (dataFrame['trend'] < 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti)
		],
		[2, 0], default=1
	)

	dataFrame['long_signal'] = np.select([dataFrame['strategy'] == 2], [-1], default=1)
	dataFrame['short_signal'] = np.select([dataFrame['strategy'] == 0], [1], default=-1)

	#testDF = dataFrame.tail(50)
	#superName = f"{strategy}_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['original'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

@njit
def adaptive_modeling(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(primaryVector)
	model = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		сutSecondary = secondaryVector[real_i-window:real_i]
		cutPrimary = primaryVector[real_i-window:real_i]
		model[i] = linearRegression(cutPrimary, сutSecondary)

	return model

@njit
def linearRegression(cutPrimary: npt.NDArray[np.float64], сutSecondary: npt.NDArray[np.float64]) -> np.float64:
	lenth = len(cutPrimary)

	if lenth < 2:
		lastValue = сutSecondary[0] if lenth == 1 else 0.0

	else:
		sum_x = 0.0
		sum_y = 0.0
		sum_xy = 0.0
		sum_x2 = 0.0
		
		for i in range(lenth):
			sum_x += cutPrimary[i]
			sum_y += сutSecondary[i]
			sum_xy += cutPrimary[i]*сutSecondary[i]
			sum_x2 += cutPrimary[i]*cutPrimary[i]
		
		denominator = lenth*sum_x2 - sum_x*sum_x
		if denominator == 0:
			lastValue = сutSecondary[-1]
		
		else:
			b = (lenth*sum_xy - sum_x*sum_y)/denominator
			a = (sum_y - b*sum_x)/lenth
			lastValue = a + b*cutPrimary[-1]
	
	return lastValue

@njit
def adaptivePriceChannel(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(closeVector)

	upLineVector = np.empty(lenth)
	meanLineVector = np.empty(lenth)
	downLineVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]

		cutOpen = openVector[real_i-window:real_i]
		cutHigh = highVector[real_i-window:real_i]
		cutLow = lowVector[real_i-window:real_i]
		cutClose = closeVector[real_i-window:real_i]

		upLineVector[i] = np.max(cutHigh)
		downLineVector[i] = np.min(cutLow)

		meanLineVector[i] = (upLineVector[i] + downLineVector[i])/2

	return upLineVector, meanLineVector, downLineVector

@njit
def adaptiveMoving(closeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)

	movingVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		movingVector[i] = np.mean(cutClose)

	return movingVector

@njit
def adaptiveRoc(closeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)

	rocVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		rocVector[i] = cutClose[-1]/cutClose[0] - 1

	return rocVector