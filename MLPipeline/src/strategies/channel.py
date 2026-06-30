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
	upLine, baseLine, downLine = adaptive_channel(closeVector=dataFrame['close'].values, windowVector=dataFrame['signal_window'].values)

	dataFrame['upLineChannel'] = upLine
	dataFrame['baseLineChannel'] = baseLine
	dataFrame['downLineChannel'] = downLine

	dataFrame['trend_window'] = (trend_window*base_volativity/dataFrame['volativity']).fillna(trend_window).astype(np.int64)
	dataFrame['trend'] = adaptive_roc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trend_window'].values)

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['close'] > dataFrame['downLineChannel']) & (dataFrame['trend'] > 0),
			(dataFrame['close'] < dataFrame['downLineChannel']) & (dataFrame['trend'] > 0)
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['close'] > dataFrame['upLineChannel']) & (dataFrame['trend'] < 0),
			(dataFrame['close'] < dataFrame['upLineChannel']) & (dataFrame['trend'] < 0)
		],
		[
			-1,
			1
		],
		default=-1
	)

	#superName = f"voladaptation_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(dataFrame['datetime'], dataFrame['close'], color="black")
	#plt.plot(dataFrame['datetime'], dataFrame['adaptive_moving'], color="red")
	#plt.plot(dataFrame['datetime'], dataFrame['signal_window'], color="orange")
	#plt.plot(dataFrame['datetime'], dataFrame['trend_window'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

@njit
def adaptive_channel(
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(closeVector)
	upLineVector = np.empty(lenth)
	baseLineVector = np.empty(lenth)
	downLineVector = np.empty(lenth)
	firstIndex = int(np.max(windowVector))

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		baseLineVector[i] = np.mean(cutClose)
		diff = np.diff(cutClose)
		abs_diff = np.abs(diff)
		average_diff = np.mean(abs_diff)
		upLineVector[i] = baseLineVector[i] + multiple*average_diff
		downLineVector[i] = baseLineVector[i] - multiple*average_diff

	return upLineVector, baseLineVector, downLineVector

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