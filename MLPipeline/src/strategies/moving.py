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

	volativityWindow = 200
	signalWindow = 20
	trendWindow = 200
	minimalMulti = 1
	baseVolativity1m = 0.0004
	baseVolativity = baseVolativity1m*convertor[timeFrame]

	dataFrame['diff'] = np.abs(dataFrame['close']/dataFrame['close'].shift(1) - 1)
	dataFrame['volativity'] = dataFrame['diff'].rolling(window=volativityWindow).mean()
	dataFrame['multiWindow'] = baseVolativity/dataFrame['volativity']

	dataFrame['signalWindow'] = (signalWindow*dataFrame['multiWindow']).fillna(signalWindow).astype(np.int64).clip(lower=2)
	dataFrame['trendWindow'] = (trendWindow*dataFrame['multiWindow']).fillna(trendWindow).astype(np.int64).clip(lower=2)

	dataFrame['adaptive_moving'] = adaptive_moving(closeVector=dataFrame['close'].values, windowVector=dataFrame['signalWindow'].values)
	dataFrame['adaptive_roc'] = adaptive_roc(closeVector=dataFrame['close'].values, windowVector=dataFrame['trendWindow'].values)

	dataFrame['strategy'] = np.select(
		[
			(dataFrame['close'] > dataFrame['adaptive_moving']) & (dataFrame['adaptive_roc'] > 0) & (dataFrame['multiWindow'] > minimalMulti),
			(dataFrame['close'] < dataFrame['adaptive_moving']) & (dataFrame['adaptive_roc'] < 0) & (dataFrame['multiWindow'] > minimalMulti)
		],
		[2, 0], default=1
	)

	dataFrame['long_signal'] = np.select([dataFrame['strategy'] == 2], [-1], default=1)
	dataFrame['short_signal'] = np.select([dataFrame['strategy'] == 0], [1], default=-1)

	#superName = f"voladaptation_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(dataFrame['datetime'], dataFrame['close'], color="black")
	#plt.plot(dataFrame['datetime'], dataFrame['adaptive_moving'], color="red")
	#plt.plot(dataFrame['datetime'], dataFrame['signalWindow'], color="orange")
	#plt.plot(dataFrame['datetime'], dataFrame['trendWindow'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]

@njit
def adaptive_moving(closeVector: npt.NDArray[np.float64], windowVector: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
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