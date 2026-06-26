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
	dataFrame['baseLine'] = adaptive_lr_curve(closeVector=dataFrame['close'].values, windowVector=dataFrame['signal_window'].values)

	dataFrame['trend_window'] = (trend_window*base_volativity/dataFrame['volativity']).fillna(trend_window).astype(np.int64)
	dataFrame['trend'] = adaptive_roc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trend_window'].values)

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['close'] > dataFrame['baseLine']) & (dataFrame['trend'] > 0),
			(dataFrame['close'] < dataFrame['baseLine']) & (dataFrame['trend'] > 0)
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['close'] > dataFrame['baseLine']) & (dataFrame['trend'] < 0),
			(dataFrame['close'] < dataFrame['baseLine']) & (dataFrame['trend'] < 0)
		],
		[
			-1,
			1
		],
		default=-1
	)

	#testDF = dataFrame.tail(50)
	#superName = f"lr_channel_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['close'], color="black")
	#plt.plot(testDF['datetime'], testDF['baseLine'], color="orange")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

@njit
def adaptive_lr_curve(
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(closeVector)
	baseLineVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		baseLineVector[i] = linearRegression(cutClose)

	return baseLineVector

@njit
def linearRegression(cutClose: npt.NDArray[np.float64]) -> np.float64:
	lenth = len(cutClose)
	if lenth < 2:
		lastValue = cutClose[0] if lenth == 1 else 0.0

	else:
		sum_x = lenth*(lenth + 1) / 2
		sum_x2 = lenth*(lenth + 1) * (2*lenth + 1)/6
		
		sum_y = 0.0
		sum_xy = 0.0
		for i in range(lenth):
			xi = i + 1
			sum_y += cutClose[i]
			sum_xy += xi*cutClose[i]
		
		denominator = lenth*sum_x2 - sum_x*sum_x
		if denominator == 0:
			lastValue = cutClose[-1]

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