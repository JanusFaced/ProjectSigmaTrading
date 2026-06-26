from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
import os
import sys
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> pd.DataFrame:

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	convertor = {
		'1min': 1,
		'2min': 2,
		'4min': 4,
		'8min': 8,
		'15min': 15,
		'30min': 30,
		'1h': 60,
		'2h': 120,
		'4h': 240,
		'6h': 360,
		'8h': 480,
		'12h': 720,
		'1d': 1440
	}

	volativity_window = 200
	signal_window = 20
	trend_window = 200
	base_volativity_1m = 0.0001
	base_volativity = base_volativity_1m*convertor[timeFrame]

	dataFrame['diff'] = np.abs(dataFrame['close']/dataFrame['close'].shift(1) - 1)
	dataFrame['volativity'] = dataFrame['diff'].rolling(window=volativity_window).mean()

	dataFrame['signal_window'] = (signal_window*base_volativity/dataFrame['volativity']).fillna(signal_window).astype(np.int64)
	dataFrame['trend_window'] = (trend_window*base_volativity/dataFrame['volativity']).fillna(trend_window).astype(np.int64)

	dataFrame['signal_diff'] = adaptive_roc(
		closeVector=dataFrame['close'].values,
		windowVector=dataFrame['signal_window'].values
	)
	dataFrame['original'] = np.abs(dataFrame['signal_diff'])

	dataFrame['primary'] = adaptive_volume(
		volumeVector=dataFrame['volume'].values,
		windowVector=dataFrame['signal_window'].values
	)

	dataFrame['model'] = adaptive_modeling(
		secondaryVector=dataFrame['original'].values,
		primaryVector=dataFrame['primary'].values,
		windowVector=dataFrame['signal_window'].values
	)

	dataFrame['trend'] = adaptive_roc(
		closeVector=dataFrame['close'].values,
		windowVector=dataFrame['trend_window'].values
	)

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['signal_diff'] > dataFrame['model']) & (dataFrame['trend'] > 0),
			(dataFrame['signal_diff'] < dataFrame['model']) & (dataFrame['trend'] > 0)
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['signal_diff'] > -dataFrame['model']) & (dataFrame['trend'] < 0),
			(dataFrame['signal_diff'] < -dataFrame['model']) & (dataFrame['trend'] < 0)
		],
		[
			-1,
			1
		],
		default=-1
	)

	#testDF = dataFrame.tail(50)
	#superName = f"{strategy}_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['diff'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="green")
	#plt.plot(testDF['datetime'], -testDF['model'], color="red")
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
def adaptive_moving(closeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)

	movingVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		movingVector[i] = np.mean(cutClose)

	return movingVector

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

@njit
def adaptive_volume(volumeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
	lenth = len(volumeVector)

	sumVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = volumeVector[real_i-window:real_i]
		sumVector[i] = np.sum(cutClose)

	return sumVector