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

	dataFrame['coloreBody'] = dataFrame['close'] - dataFrame['open']
	dataFrame['sizeBody'] = np.abs(dataFrame['coloreBody'])
	
	dataFrame['sizeUpWick'] = np.select(
		[
			dataFrame['coloreBody'] > 0,
			dataFrame['coloreBody'] < 0
		],
		[
			dataFrame['high'] - dataFrame['close'],
			dataFrame['high'] - dataFrame['open']
		],
		default=0.0
	)

	dataFrame['sizeDownWick'] = np.select(
		[
			dataFrame['coloreBody'] > 0,
			dataFrame['coloreBody'] < 0
		],
		[
			dataFrame['open'] - dataFrame['low'],
			dataFrame['close'] - dataFrame['low']
		],
		default=0.0
	)

	dataFrame['coloreBody1'] = dataFrame['coloreBody'].shift(1)
	dataFrame['sizeBody1'] = dataFrame['sizeBody'].shift(1)
	dataFrame['coloreBody2'] = dataFrame['coloreBody'].shift(2)
	dataFrame['sizeBody2'] = dataFrame['sizeBody'].shift(2)

	dataFrame['high1'] = dataFrame['high'].shift(1)
	dataFrame['high2'] = dataFrame['high'].shift(2)
	dataFrame['high3'] = dataFrame['high'].shift(3)
	dataFrame['high4'] = dataFrame['high'].shift(4)

	dataFrame['low1'] = dataFrame['low'].shift(1)
	dataFrame['low2'] = dataFrame['low'].shift(2)
	dataFrame['low3'] = dataFrame['low'].shift(3)
	dataFrame['low4'] = dataFrame['low'].shift(4)

	dataFrame['pinbar'] = np.select(
		[
			(dataFrame['coloreBody'] > 0) & (dataFrame['sizeDownWick'] > dataFrame['sizeBody']) & (dataFrame['sizeBody'] > dataFrame['sizeUpWick']),
			(dataFrame['coloreBody'] < 0) & (dataFrame['sizeDownWick'] < dataFrame['sizeBody']) & (dataFrame['sizeBody'] < dataFrame['sizeUpWick'])
		],
		[-1, 1], default=0
	)

	dataFrame['engulfing'] = np.select(
		[
			(dataFrame['sizeBody'] > dataFrame['sizeBody1']) & (dataFrame['coloreBody'] > 0) & (dataFrame['coloreBody1'] < 0),
			(dataFrame['sizeBody'] > dataFrame['sizeBody1']) & (dataFrame['coloreBody'] < 0) & (dataFrame['coloreBody1'] > 0)
		],
		[-1, 1], default=0
	)

	dataFrame['star'] = np.select(
		[
			(dataFrame['sizeBody'] > dataFrame['sizeBody2']) & (dataFrame['sizeBody2'] > dataFrame['sizeBody1']) & (dataFrame['coloreBody'] > 0) & (dataFrame['coloreBody2'] < 0),
			(dataFrame['sizeBody'] > dataFrame['sizeBody2']) & (dataFrame['sizeBody2'] > dataFrame['sizeBody1']) & (dataFrame['coloreBody'] < 0) & (dataFrame['coloreBody2'] > 0)
		],
		[-1, 1], default=0
	)

	dataFrame['fractal'] = np.select(
		[
			(dataFrame['low2'] < dataFrame['low']) & (dataFrame['low2'] < dataFrame['low1']) & (dataFrame['low2'] < dataFrame['low3']) & (dataFrame['low2'] < dataFrame['low4']),
			(dataFrame['high2'] > dataFrame['high']) & (dataFrame['high2'] > dataFrame['high1']) & (dataFrame['high2'] > dataFrame['high3']) & (dataFrame['high2'] > dataFrame['high4']),
		],
		[-1, 1], default=0
	)

	dataFrame['soldiers'] = np.select(
		[
			(dataFrame['coloreBody'] > 0) & (dataFrame['coloreBody1'] > 0) & (dataFrame['coloreBody2'] > 0),
			(dataFrame['coloreBody'] < 0) & (dataFrame['coloreBody1'] < 0) & (dataFrame['coloreBody2'] < 0),
		],
		[-1, 1], default=0
	)

	dataFrame['long_pattern'] = np.select(
		[(dataFrame['pinbar'] == -1) | (dataFrame['engulfing'] == -1) | (dataFrame['star'] == -1) | (dataFrame['fractal'] == -1) | (dataFrame['soldiers'] == -1)],
		[-1], default=0
	)

	dataFrame['short_pattern'] = np.select(
		[(dataFrame['pinbar'] == 1) | (dataFrame['engulfing'] == 1) | (dataFrame['star'] == 1) | (dataFrame['fractal'] == 1) | (dataFrame['soldiers'] == 1)],
		[1], default=0
	)

	dataFrame['pattern'] = np.select(
		[
			(dataFrame['long_pattern'] == -1) & (dataFrame['short_pattern'] == 0),
			(dataFrame['short_pattern'] == 1) & (dataFrame['long_pattern'] == 0),
		],
		[-1, 1], default=0
	)

	dataFrame['upLine'], dataFrame['meanLine'], dataFrame['downLine'] = adaptivePriceChannel(
		openVector=dataFrame['open'].values,
		highVector=dataFrame['high'].values,
		lowVector=dataFrame['low'].values,
		closeVector=dataFrame['close'].values,
		windowVector=dataFrame['signalWindow'].values
	)
	dataFrame['upLineOld'] = dataFrame['upLine'].shift(1)
	dataFrame['downLineOld'] = dataFrame['downLine'].shift(1)
	
	dataFrame['trend'] = adaptiveRoc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trendWindow'].values)

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['pattern'] == -1),
			(dataFrame['close'] < dataFrame['downLineOld'])
		],
		[-1, 1], default=1
	)
	
	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['pattern'] == 1),
			(dataFrame['close'] > dataFrame['upLineOld'])
		],
		[1, -1], default=-1
	)

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['trend'] > 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti)
		],
		[dataFrame['long_signal']], default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['trend'] < 0) & (maxMulti > dataFrame['window']) & (dataFrame['window'] > minMulti)
		],
		[dataFrame['short_signal']], default=-1
	)

	#superName = f"voladaptation_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(dataFrame['datetime'], dataFrame['signalWindow'], color="orange")
	#plt.plot(dataFrame['datetime'], dataFrame['trendWindow'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

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