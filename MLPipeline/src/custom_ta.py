from typing import Any, TypedDict
import numpy as np
import numpy.typing as npt
from numba import njit

@njit(cache=True)
def adaptive_moving(
		closeVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16]
	) -> npt.NDArray[np.float32]:
	lenth = len(closeVector)
	movingVector = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		movingVector[i] = np.mean(cutClose)
	return movingVector

@njit(cache=True)
def adaptive_roc(
		closeVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16]
	) -> npt.NDArray[np.float32]:
	lenth = len(closeVector)
	rocVector = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		rocVector[i] = cutClose[-1]/cutClose[0] - 1
	return rocVector

@njit(cache=True)
def adaptive_lr_channel(
		closeVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32], npt.NDArray[np.float32]]:
	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float32)
	baseLineVector = np.empty(lenth, dtype=np.float32)
	downLineVector = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		baseLineVector[i] = linearRegression(cutClose)
		diff = np.diff(cutClose)
		abs_diff = np.abs(diff)
		average_diff = np.mean(abs_diff)
		upLineVector[i] = baseLineVector[i] + multiple*average_diff
		downLineVector[i] = baseLineVector[i] - multiple*average_diff
	return upLineVector, baseLineVector, downLineVector

@njit(cache=True)
def adaptive_lr_forecast(
		diffVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16]
	) -> npt.NDArray[np.float32]:
	lenth = len(diffVector)
	modelLineVector = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i
		window = windowVector[i]
		cutWindow = diffVector[real_i-window:real_i]
		modelLineVector[i] = linearRegression(cutWindow)
	return modelLineVector

@njit(cache=True)
def linearRegression(cutClose: npt.NDArray[np.float32]) -> np.float32:
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

@njit(cache=True)
def adaptive_modeling_volume(
		secondaryVector: npt.NDArray[np.float32],
		primaryVector: npt.NDArray[np.int64],
		windowVector: npt.NDArray[np.int16],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
	lenth = len(primaryVector)
	p_model = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		сutSecondary = secondaryVector[real_i-window:real_i]
		cutPrimary = primaryVector[real_i-window:real_i]
		p_model[i] = lr_modeling_volume(cutPrimary, сutSecondary)
	n_model = -1*p_model
	return p_model, n_model

@njit(cache=True)
def lr_modeling_volume(
		cutPrimary: npt.NDArray[np.int64],
		сutSecondary: npt.NDArray[np.float32]
	) -> np.float32:
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

@njit(cache=True)
def adaptive_modeling_correlation(
		secondaryVector: npt.NDArray[np.float32],
		primaryVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32], npt.NDArray[np.float32]]:
	lenth = len(primaryVector)
	model = np.empty(lenth, dtype=np.float32)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		сutSecondary = secondaryVector[real_i-window:real_i]
		cutPrimary = primaryVector[real_i-window:real_i]
		model[i] = lr_modeling_correlation(cutPrimary, сutSecondary)
	return model

@njit(cache=True)
def lr_modeling_correlation(
		cutPrimary: npt.NDArray[np.float32],
		сutSecondary: npt.NDArray[np.float32]
	) -> np.float32:
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

@njit(cache=True)
def adaptive_volume(
		volumeVector: npt.NDArray[np.int64],
		windowVector: npt.NDArray[np.int16]
	) -> npt.NDArray[np.int64]:
	lenth = len(volumeVector)
	sumVector = np.empty(lenth, dtype=np.int64)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = volumeVector[real_i-window:real_i]
		sumVector[i] = np.sum(cutClose)
	return sumVector

@njit(cache=True)
def adaptive_price_channel(
		openVector: npt.NDArray[np.float32],
		highVector: npt.NDArray[np.float32],
		lowVector: npt.NDArray[np.float32],
		closeVector: npt.NDArray[np.float32],
		windowVector: npt.NDArray[np.int16]
	) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32], npt.NDArray[np.float32]]:
	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float32)
	meanLineVector = np.empty(lenth, dtype=np.float32)
	downLineVector = np.empty(lenth, dtype=np.float32)
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