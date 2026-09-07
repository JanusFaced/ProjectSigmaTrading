from typing import Any, TypedDict
from convertorTF import convertorTimeFrame
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import time
from pathlib import Path
from logger_setup import get_logger

logger = get_logger(__name__)
output_dir = Path(__file__).parent.parent / "output"

@njit(cache=True)
def linearRegression(cutClose: npt.NDArray[np.float64]) -> np.float64:
	length = len(cutClose)
	if length < 2:
		lastValue = cutClose[0] if length == 1 else 0.0
	else:
		sum_x = length*(length + 1) / 2
		sum_x2 = length*(length + 1) * (2*length + 1)/6
		sum_y = 0.0
		sum_xy = 0.0
		for i in range(length):
			xi = i + 1
			sum_y += cutClose[i]
			sum_xy += xi*cutClose[i]
		denominator = length*sum_x2 - sum_x*sum_x
		if denominator == 0:
			lastValue = cutClose[-1]
		else:
			parametr_b = (length * sum_xy - sum_x * sum_y) / denominator
			parametr_a = (sum_y - parametr_b * sum_x) / length
			lastValue = parametr_a + parametr_b*length
	return lastValue

@njit(cache=True)
def lr_correlation(
		cutPrimary: npt.NDArray[np.float64],
		сutSecondary: npt.NDArray[np.float64]
	) -> np.float64:
	length = len(cutPrimary)
	if length < 2:
		lastValue = сutSecondary[0] if length == 1 else 0.0
	else:
		sum_x = 0.0
		sum_y = 0.0
		sum_xy = 0.0
		sum_x2 = 0.0
		for i in range(length):
			sum_x += cutPrimary[i]
			sum_y += сutSecondary[i]
			sum_xy += cutPrimary[i]*сutSecondary[i]
			sum_x2 += cutPrimary[i]*cutPrimary[i]
		denominator = length*sum_x2 - sum_x*sum_x
		if denominator == 0:
			lastValue = сutSecondary[-1]
		else:
			b = (length*sum_xy - sum_x*sum_y)/denominator
			a = (sum_y - b*sum_x)/length
			lastValue = a + b*cutPrimary[-1]
	return lastValue

@njit(cache=True)
def simple_linear_regression(
		closeVector: npt.NDArray[np.float64],
		baseWindow: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	curveVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = baseWindow

	for i in range(firstIndex, length):
		real_i = i+1
		window = baseWindow
		cutWindow = closeVector[real_i-window:real_i]
		curveVector[i] = linearRegression(cutWindow)

	return curveVector

@njit(cache=True)
def simple_correlation(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		baseWindow: int = 20
	) -> npt.NDArray[np.float64]:

	length = len(primaryVector)
	model = np.full(length, np.nan, dtype=np.float64)
	firstIndex = baseWindow
	for i in range(firstIndex, length):
		real_i = i+1
		window = baseWindow
		cutSecondary = secondaryVector[real_i-window:real_i]
		cutPrimary = primaryVector[real_i-window:real_i]
		model[i] = lr_correlation(cutPrimary, cutSecondary)
	
	return model

@njit(cache=True)
def covertToStatic(vector: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
	diff = vector[1:] - vector[:-1]
	trend = np.mean(diff)
	clearDiff = diff - trend
	vector = np.concatenate((
		np.array([vector[0]]),
		np.cumsum(clearDiff) + vector[0]
	))
	return vector

@njit(cache=True)
def zScoreNormalize(vector: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
	mean = np.mean(vector)
	std = np.std(vector)
	vector = (vector - mean)/std
	return vector

@njit(cache=True)
def correlationPirson(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		baseWindow: int = 20
	) -> npt.NDArray[np.float64]:

	length = len(primaryVector)
	corrVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = baseWindow

	for i in range(firstIndex, length):
		real_i = i+1
		window = baseWindow
		cutPrimary = primaryVector[real_i-window:real_i]
		cutSecondary = secondaryVector[real_i-window:real_i]

		staticPrimary = covertToStatic(cutPrimary)
		staticSecondary = covertToStatic(cutSecondary)

		corrVector[i] = np.corrcoef(staticPrimary, staticSecondary)[0][1]
	
	return corrVector

@njit(cache=True)
def spreadMaker(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		baseWindow: int = 20
	) -> npt.NDArray[np.float64]:

	length = len(primaryVector)
	spreadVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = baseWindow

	for i in range(firstIndex, length):
		real_i = i+1
		window = baseWindow
		cutPrimary = primaryVector[real_i-window:real_i]
		cutSecondary = secondaryVector[real_i-window:real_i]

		normPrimary = zScoreNormalize(cutPrimary)
		normSecondary = zScoreNormalize(cutSecondary)

		normPrimary = normPrimary - normPrimary[0]
		normSecondary = normSecondary - normSecondary[0]

		spreadVector[i] = normSecondary[-1] - normPrimary[-1]
	
	return spreadVector

@njit(cache=True)
def hurstCoef(
		closeVector: npt.NDArray[np.float64],
		window: int = 200,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	hurstVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	eps = 1e-10
	
	for i in range(firstIndex, length):
		real_i = i+1
		cutPrice = closeVector[real_i-window:real_i]
		x_series = np.diff(np.log(cutPrice))
		hurst_n = len(x_series)
		x_mean = np.mean(x_series)
		y_series = np.cumsum(x_series - x_mean)
		hurst_R = np.max(y_series) - np.min(y_series)
		hurst_S = np.sqrt(np.sum((x_series - x_mean)**2) / (hurst_n - 1))
		hurstVector[i] = np.log(max(hurst_R, eps)/max(hurst_S, eps))/np.log(hurst_n)

	return hurstVector

@njit(cache=True)
def kamaInd(
		closeVector: npt.NDArray[np.float64],
		scVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	kamaVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	
	for i in range(firstIndex, length):
		real_i = i+1
		pastKama = (
			kamaVector[i-1] if i > firstIndex
			else np.mean(closeVector[real_i-window:real_i])
		)
		kamaVector[i] = pastKama + scVector[i]*(closeVector[i] - pastKama)

	return kamaVector

@njit(cache=True)
def pattern_soldiers(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	patternVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	baseWindow = 20
	convertor = int(window/baseWindow)

	for i in range(firstIndex, length):
		real_i = i+1

		start_i_0 = i
		end_i_0 = start_i_0 + 1 - convertor
		
		start_i_1 = end_i_0 - 1
		end_i_1 = start_i_1 + 1 - convertor
		
		start_i_2 = end_i_1 - 1
		end_i_2 = start_i_2 + 1 - convertor

		colorCandle0 = closeVector[start_i_0] - openVector[end_i_0]
		colorCandle1 = closeVector[start_i_1] - openVector[end_i_1]
		colorCandle2 = closeVector[start_i_2] - openVector[end_i_2]

		allPositive = (colorCandle0 > 0) and (colorCandle1 > 0) and (colorCandle2 > 0)
		allNegative = (colorCandle0 < 0) and (colorCandle1 < 0) and (colorCandle2 < 0)

		patternVector[i] = -1 if allPositive else 1 if allNegative else 0

	return patternVector

@njit(cache=True)
def pattern_engulfing(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	patternVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	baseWindow = 20
	convertor = int(window/baseWindow)

	for i in range(firstIndex, length):
		real_i = i+1

		start_i_0 = i
		end_i_0 = start_i_0 + 1 - convertor
		
		start_i_1 = end_i_0 - 1
		end_i_1 = start_i_1 + 1 - convertor

		colorCandle0 = closeVector[start_i_0] - openVector[end_i_0]
		colorCandle1 = closeVector[start_i_1] - openVector[end_i_1]

		allPositive = (colorCandle0 > 0) and (colorCandle1 < 0) and (np.abs(colorCandle0) > np.abs(colorCandle1))
		allNegative = (colorCandle0 < 0) and (colorCandle1 > 0) and (np.abs(colorCandle0) > np.abs(colorCandle1))

		patternVector[i] = -1 if allPositive else 1 if allNegative else 0

	return patternVector

@njit(cache=True)
def pattern_star(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	patternVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	baseWindow = 20
	convertor = int(window/baseWindow)

	for i in range(firstIndex, length):
		real_i = i+1

		start_i_0 = i
		end_i_0 = start_i_0 + 1 - convertor
		
		start_i_1 = end_i_0 - 1
		end_i_1 = start_i_1 + 1 - convertor
		
		start_i_2 = end_i_1 - 1
		end_i_2 = start_i_2 + 1 - convertor

		colorCandle0 = closeVector[start_i_0] - openVector[end_i_0]
		colorCandle1 = closeVector[start_i_1] - openVector[end_i_1]
		colorCandle2 = closeVector[start_i_2] - openVector[end_i_2]

		sizeCandle0 = np.abs(colorCandle0)
		sizeCandle1 = np.abs(colorCandle1)
		sizeCandle2 = np.abs(colorCandle2)

		buyLogic = (sizeCandle1 < sizeCandle0) and (sizeCandle1 < sizeCandle2) and (colorCandle2 < 0) and (colorCandle0 > 0)
		sellLogic = (sizeCandle1 < sizeCandle0) and (sizeCandle1 < sizeCandle2) and (colorCandle2 > 0) and (colorCandle0 < 0)

		patternVector[i] = -1 if buyLogic else 1 if sellLogic else 0

	return patternVector

@njit(cache=True)
def pattern_pinbar(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	patternVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	baseWindow = 20
	convertor = int(window/baseWindow)

	for i in range(firstIndex, length):
		real_i = i+1

		start_i_0 = i
		end_i_0 = start_i_0 + 1 - convertor

		colorCandle0 = closeVector[start_i_0] - openVector[end_i_0]

		sizeBody0 = np.abs(colorCandle0)
		high0 = np.max(highVector[end_i_0:start_i_0+1])
		low0 = np.min(lowVector[end_i_0:start_i_0+1])

		sizeUpWick0 = np.abs(high0 - max(closeVector[start_i_0], openVector[end_i_0]))
		sizeDownWick0 = np.abs(low0 - min(closeVector[start_i_0], openVector[end_i_0]))

		buyLogic = (sizeUpWick0 < sizeBody0) and (sizeBody0 < sizeDownWick0)
		sellLogic = (sizeDownWick0 < sizeBody0) and (sizeBody0 < sizeUpWick0)

		patternVector[i] = -1 if buyLogic else 1 if sellLogic else 0

	return patternVector

@njit(cache=True)
def pattern_fractal(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(closeVector)
	patternVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window
	baseWindow = 20
	convertor = int(window/baseWindow)

	for i in range(firstIndex, length):
		real_i = i+1

		start_i_0 = i
		end_i_0 = start_i_0 + 1 - convertor
		
		start_i_1 = end_i_0 - 1
		end_i_1 = start_i_1 + 1 - convertor

		start_i_2 = end_i_1 - 1
		end_i_2 = start_i_2 + 1 - convertor

		start_i_3 = end_i_2 - 1
		end_i_3 = start_i_3 + 1 - convertor

		start_i_4 = end_i_3 - 1
		end_i_4 = start_i_4 + 1 - convertor

		high0 = np.max(highVector[end_i_0:start_i_0+1])
		high1 = np.max(highVector[end_i_1:start_i_1+1])
		high2 = np.max(highVector[end_i_2:start_i_2+1])
		high3 = np.max(highVector[end_i_3:start_i_3+1])
		high4 = np.max(highVector[end_i_4:start_i_4+1])

		low0 = np.min(lowVector[end_i_0:start_i_0+1])
		low1 = np.min(lowVector[end_i_1:start_i_1+1])
		low2 = np.min(lowVector[end_i_2:start_i_2+1])
		low3 = np.min(lowVector[end_i_3:start_i_3+1])
		low4 = np.min(lowVector[end_i_4:start_i_4+1])

		upFractal = (high2 > high0) and (high2 > high1) and (high2 > high3) and (high2 > high4)
		downFractal = (low2 < low0) and (low2 < low1) and (low2 < low3) and (low2 < low4)

		patternVector[i] = -1 if (downFractal and not(upFractal)) else 1 if (upFractal and not(downFractal)) else 0

	return patternVector


@njit(cache=True)
def zigzag(
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		pattern: npt.NDArray[np.float64],
		window: int = 20,
	) -> npt.NDArray[np.float64]:

	length = len(pattern)
	zigZagMode = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window

	oldUpFractal0 = highVector[1]
	oldDownFractal0 = lowVector[1]

	oldUpFractal1 = highVector[0]
	oldDownFractal1 = lowVector[0]

	for i in range(firstIndex, length):

		currentUpFractal = highVector[i] if pattern[i] == 1 else -100
		currentDownFractal = lowVector[i] if pattern[i] == -1 else -100

		if currentUpFractal > 0.00:
			oldUpFractal1 = oldUpFractal0
			oldUpFractal0 = currentUpFractal

		if currentDownFractal > 0.00:
			oldDownFractal1 = oldDownFractal0
			oldDownFractal0 = currentDownFractal

		deltaUp = oldUpFractal0 - oldUpFractal1
		deltaDown = oldDownFractal0 - oldDownFractal1

		zigZagMode[i] = -1 if ((deltaUp > 0) and (deltaDown > 0 )) else 1 if ((deltaUp < 0) and (deltaDown < 0 )) else 0

	return zigZagMode

@njit(cache=True)
def makeLine(
		y0: float,
		y1: float,
		x0: int,
		x1: int,
		xC: int,
	) -> float:

	b = (y1 - y0) / (x1 - x0)
	a = y0 - x0*b
	yC = a + xC*b

	return yC

@njit(cache=True)
def zzChannel(
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		pattern: npt.NDArray[np.float64],
		window: int = 20,
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:

	length = len(pattern)
	zzUpLine = np.full(length, np.nan, dtype=np.float64)
	zzDownLine = np.full(length, np.nan, dtype=np.float64)
	firstIndex = window

	points = {
		"oldUpFractal0": {"value": highVector[1], "point": 1,},
		"oldDownFractal0": {"value": lowVector[1], "point": 1,},
		"oldUpFractal1": {"value": highVector[0], "point": 0,},
		"oldDownFractal1": {"value": lowVector[0], "point": 0,},
	}

	for i in range(firstIndex, length):

		currentUpFractalValue = highVector[i] if pattern[i] == 1 else -100
		currentDownFractalValue = lowVector[i] if pattern[i] == -1 else -100

		currentUpFractalPoint = i if pattern[i] == 1 else -100
		currentDownFractalPoint = i if pattern[i] == -1 else -100

		if currentUpFractalValue > 0.00:
			points["oldUpFractal1"]["value"] = points["oldUpFractal0"]["value"]
			points["oldUpFractal0"]["value"] = currentUpFractalValue

			points["oldUpFractal1"]["point"] = points["oldUpFractal0"]["point"]
			points["oldUpFractal0"]["point"] = currentUpFractalPoint

		if currentDownFractalValue > 0.00:
			points["oldDownFractal1"]["value"] = points["oldDownFractal0"]["value"]
			points["oldDownFractal0"]["value"] = currentDownFractalValue

			points["oldDownFractal1"]["point"] = points["oldDownFractal0"]["point"]
			points["oldDownFractal0"]["point"] = currentDownFractalPoint

		zzUpLine[i] = makeLine(
			y0=points["oldUpFractal1"]["value"],
			y1=points["oldUpFractal0"]["value"],
			x0=points["oldUpFractal1"]["point"],
			x1=points["oldUpFractal0"]["point"],
			xC=i,
		)
		
		zzDownLine[i] = makeLine(
			y0=points["oldDownFractal1"]["value"],
			y1=points["oldDownFractal0"]["value"],
			x0=points["oldDownFractal1"]["point"],
			x1=points["oldDownFractal0"]["point"],
			xC=i,
		)

	return zzUpLine, zzDownLine

