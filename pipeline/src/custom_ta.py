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
def normalize(cutWindow):
	maxValue = np.max(cutWindow)
	minValue = np.min(cutWindow)
	return (cutWindow - minValue)/(maxValue - minValue)

@njit(cache=True)
def correlation_pirson(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		baseWindow: int = 20
	) -> npt.NDArray[np.float64]:

	length = len(primaryVector)
	corrVector = np.full(length, np.nan, dtype=np.float64)
	spreadVector = np.full(length, np.nan, dtype=np.float64)
	firstIndex = baseWindow
	for i in range(firstIndex, length):
		real_i = i+1
		window = baseWindow
		cutPrimary = primaryVector[real_i-window:real_i]
		cutSecondary = secondaryVector[real_i-window:real_i]

		corr = np.corrcoef(cutPrimary, cutSecondary)[0][1]

		normCutPrimary = normalize(cutPrimary)
		normCutSecondary = normalize(cutSecondary)

		spread = normCutPrimary[-1] - normCutSecondary[-1]

		corrVector[i] = corr
		spreadVector[i] = spread
	
	return corrVector, spreadVector

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





