from typing import Any, TypedDict
import numpy as np
import numpy.typing as npt
from numba import njit
import time

@njit(cache=True)
def hotResampler(
		baseVector: npt.NDArray[np.float64],
		relativeTimeFrame: int,
		resamplMode: str
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(baseVector)

	finalVector = np.empty(lenth, dtype=np.float64)

	tempStart = 0
	tempMax = 0
	tempMin = 0
	tempEnd = 0
	tempSum = 0
	counter = 0
	for i in range(len(baseVector)):

		startIndex = 0
		endIndex = relativeTimeFrame-1
		pastIndex = len(baseVector)-1
		timeToEnd = pastIndex - i

		if resamplMode == 'start':
			if counter == startIndex:
				preTempStart = baseVector[i]
			elif counter == endIndex:
				tempStart = preTempStart if (timeToEnd >= relativeTimeFrame) else tempStart
			finalVector[i] = tempStart
 
		elif resamplMode == 'max':
			if counter == startIndex:
				preTempMax = baseVector[i]
			elif endIndex >= counter > startIndex:
				preTempMax = preTempMax if preTempMax > baseVector[i] else baseVector[i]
			if counter == endIndex:
				tempMax = preTempMax if (timeToEnd >= relativeTimeFrame) else tempMax
			finalVector[i] = tempMax

		elif resamplMode == 'min':
			if counter == startIndex:
				preTempMin = baseVector[i]
			elif endIndex >= counter > startIndex:
				preTempMin = preTempMin if preTempMin < baseVector[i] else baseVector[i]
			if counter == endIndex:
				tempMin = preTempMin if (timeToEnd >= relativeTimeFrame) else tempMin
			finalVector[i] = tempMin

		elif resamplMode == 'end':
			if counter == endIndex:
				tempEnd = baseVector[i] if (timeToEnd >= relativeTimeFrame) else tempEnd
			finalVector[i] = tempEnd

		elif resamplMode == 'sum':
			if counter == startIndex:
				preTempSum = baseVector[i]
			elif endIndex >= counter > startIndex:
				preTempSum += baseVector[i]
			if counter == endIndex:
				tempSum = preTempSum if (timeToEnd >= relativeTimeFrame) else tempSum
			finalVector[i] = tempSum

		counter += 1
		if counter == relativeTimeFrame:
			counter = 0
	
	return finalVector

@njit(cache=True)
def concentrator(
		preCutWindow: npt.NDArray[np.float64],
		numberMissing: int
	) -> npt.NDArray[np.float64]:
	cutWindow = np.empty(0, dtype=np.float64)
	counter = 0
	for i in range(len(preCutWindow)):
		if counter == numberMissing:
			cutWindow = np.append(cutWindow, preCutWindow[i])
		counter += 1
		if counter == numberMissing+1:
			counter = 0
	return cutWindow

@njit(cache=True)
def adaptive_moving(
		closeVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int,
		depth: int
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:

	lenth = len(closeVector)
	movingVector = np.empty(lenth, dtype=np.float64)
	movingDiffVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	matrix = [closeVector]
	for i in range(depth):
		relativeTimeFrame = 2**(depth+1)
		resamplVector = hotResampler(
			baseVector=closeVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		matrix.append(resamplVector)

	for i in range(firstIndex, lenth):
		real_i = i+1
		multi = volMulti[i] if volMulti[i] > 1.0 else 1.0
		window = int(baseWindow*multi)
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		preCutWindow = matrix[address][real_i-window:real_i]
		
		cutWindow = concentrator(preCutWindow=preCutWindow, numberMissing=address)
		currentMoving = np.mean(cutWindow) if len(cutWindow) > 2 else 0

		preCutWindow = matrix[address][i-window:i]
		cutWindow = concentrator(preCutWindow=preCutWindow, numberMissing=address)
		pastMoving = np.mean(cutWindow) if len(cutWindow) > 2 else 0

		movingVector[i] = currentMoving
		movingDiffVector[i] = currentMoving - pastMoving

	return movingVector, movingDiffVector

@njit(cache=True)
def adaptive_adx(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(closeVector)
	posDmiVector = np.empty(lenth, dtype=np.float64)
	negDmiVector = np.empty(lenth, dtype=np.float64)
	adxVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutOpen = openVector[real_i-window:real_i]
		cutHigh = highVector[real_i-window:real_i]
		cutLow = lowVector[real_i-window:real_i]
		cutClose = closeVector[real_i-window:real_i]
		cutTrueRange = (cutHigh - cutLow)[1:]
		cutPosM = cutHigh[1:] - cutHigh[:-1]
		cutNegM = cutLow[:-1] - cutLow[1:]
		cutPosDM = np.where((cutPosM > cutNegM) & (cutPosM > 0), cutPosM, 0.0)
		cutNegDM = np.where((cutNegM > cutPosM) & (cutNegM > 0), cutNegM, 0.0)
		posDmiVector[i] = np.mean(cutPosDM)/np.mean(cutTrueRange)
		negDmiVector[i] = np.mean(cutNegDM)/np.mean(cutTrueRange)

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutPosDI = posDmiVector[real_i-window:real_i]
		cutNegDI = negDmiVector[real_i-window:real_i]
		cutDXI = 100*np.abs(cutPosDI - cutNegDI)/(cutPosDI + cutNegDI)
		adxVector[i] = np.mean(cutDXI)
	
	return posDmiVector, negDmiVector, adxVector

@njit(cache=True)
def adaptive_bollinger(
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float64)
	movingVector = np.empty(lenth, dtype=np.float64)
	downLineVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		movingVector[i] = np.mean(cutClose)
		sigma = np.std(cutClose)
		upLineVector[i] = movingVector[i] + sigma
		downLineVector[i] = movingVector[i] - sigma
	return upLineVector, movingVector, downLineVector

@njit(cache=True)
def adaptive_roc(
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)
	rocVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = windowVector[i]
		cutClose = closeVector[real_i-window:real_i]
		rocVector[i] = cutClose[-1]/cutClose[0] - 1
	return rocVector

@njit(cache=True)
def adaptive_lr_channel(
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float64)
	baseLineVector = np.empty(lenth, dtype=np.float64)
	downLineVector = np.empty(lenth, dtype=np.float64)
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
		diffVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> npt.NDArray[np.float64]:
	lenth = len(diffVector)
	modelLineVector = np.empty(lenth, dtype=np.float64)
	firstIndex = int(np.max(windowVector))
	for i in range(firstIndex, lenth):
		real_i = i
		window = windowVector[i]
		cutWindow = diffVector[real_i-window:real_i]
		modelLineVector[i] = linearRegression(cutWindow)
	return modelLineVector

@njit(cache=True)
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

@njit(cache=True)
def adaptive_modeling_volume(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.int64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(primaryVector)
	p_model = np.empty(lenth, dtype=np.float64)
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
		сutSecondary: npt.NDArray[np.float64]
	) -> np.float64:
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
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64],
		multiple: float = 1.00
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(primaryVector)
	model = np.empty(lenth, dtype=np.float64)
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
		cutPrimary: npt.NDArray[np.float64],
		сutSecondary: npt.NDArray[np.float64]
	) -> np.float64:
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
		windowVector: npt.NDArray[np.int64]
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
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		windowVector: npt.NDArray[np.int64]
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float64)
	meanLineVector = np.empty(lenth, dtype=np.float64)
	downLineVector = np.empty(lenth, dtype=np.float64)
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