from typing import Any, TypedDict
import numpy as np
import numpy.typing as npt
from numba import njit
import time

#start technical functions
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
def lr_correlation(
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

#end technical functions

#start indicators
@njit(cache=True)
def adaptive_moving(
		closeVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int = 20,
		multiple: float = 1.00,
		baseLineMode: str = "MA",
		depth: int = 0
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:

	lenth = len(closeVector)
	upLineVector = np.empty(lenth, dtype=np.float64)
	movingVector = np.empty(lenth, dtype=np.float64)
	downLineVector = np.empty(lenth, dtype=np.float64)
	movingDiffVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	matrix = [closeVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=closeVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		matrix.append(resamplVector)

	for i in range(firstIndex, lenth):
		real_i = i+1
		multi = volMulti[i]
		window = int(baseWindow*multi) if int(baseWindow*multi) > 2 else 2
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		currentPreCutWindow = matrix[address][real_i-window:real_i]
		pastPreCutWindow = matrix[address][i-window:i]
		
		currentCutWindow = concentrator(preCutWindow=currentPreCutWindow, numberMissing=address)
		pastCutWindow = concentrator(preCutWindow=pastPreCutWindow, numberMissing=address)

		if baseLineMode == "MA":
			currentLine = np.mean(currentCutWindow) if len(currentCutWindow) > 2 else 0
			pastLine = np.mean(pastCutWindow) if len(pastCutWindow) > 2 else 0

		elif baseLineMode == "LR":
			currentLine = linearRegression(currentCutWindow) if len(currentCutWindow) > 2 else 0
			pastLine = linearRegression(pastCutWindow) if len(pastCutWindow) > 2 else 0

		movingVector[i] = currentLine
		movingDiffVector[i] = currentLine - pastLine

		sigma = np.std(currentCutWindow) if len(currentCutWindow) > 2 else 0
		upLineVector[i] = currentLine + multiple*sigma
		downLineVector[i] = currentLine - multiple*sigma

	return upLineVector, movingVector, downLineVector, movingDiffVector

@njit(cache=True)
def simple_linear_regression(
		closeVector: npt.NDArray[np.float64],
		baseWindow: int = 20,
	) -> npt.NDArray[np.float64]:

	lenth = len(closeVector)
	curveVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow

	for i in range(firstIndex, lenth):
		real_i = i+1
		window = baseWindow
		cutWindow = closeVector[real_i-window:real_i]
		curveVector[i] = linearRegression(cutWindow)

	return curveVector

@njit(cache=True)
def adaptive_adx(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int = 20,
		depth: int = 0
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
	
	lenth = len(closeVector)
	posDmiVector = np.empty(lenth, dtype=np.float64)
	negDmiVector = np.empty(lenth, dtype=np.float64)
	adxVector = np.empty(lenth, dtype=np.float64)
	adxDiffVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	openMatrix = [openVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=openVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='start'
		)
		openMatrix.append(resamplVector)

	highMatrix = [highVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=highVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='max'
		)
		highMatrix.append(resamplVector)

	lowMatrix = [lowVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=lowVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='min'
		)
		lowMatrix.append(resamplVector)

	closeMatrix = [closeVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=closeVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		closeMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):

		real_i = i+1
		multi = volMulti[i]
		window = int(baseWindow*multi) if int(baseWindow*multi) > 3 else 3
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		preCutOpen = openMatrix[address][real_i-window:real_i]
		preCutHigh = highMatrix[address][real_i-window:real_i]
		preCutLow = lowMatrix[address][real_i-window:real_i]
		preCutClose = closeMatrix[address][real_i-window:real_i]

		cutOpen = concentrator(preCutWindow=preCutOpen, numberMissing=address)
		cutHigh = concentrator(preCutWindow=preCutHigh, numberMissing=address)
		cutLow = concentrator(preCutWindow=preCutLow, numberMissing=address)
		cutClose = concentrator(preCutWindow=preCutClose, numberMissing=address)

		cutTrueRange = (cutHigh - cutLow)[1:]
		cutPosM = cutHigh[1:] - cutHigh[:-1]
		cutNegM = cutLow[:-1] - cutLow[1:]
		cutPosDM = np.where((cutPosM > cutNegM) & (cutPosM > 0), cutPosM, 0.0)
		cutNegDM = np.where((cutNegM > cutPosM) & (cutNegM > 0), cutNegM, 0.0)
		ATR = np.mean(cutTrueRange)
		posDmiVector[i] = np.mean(cutPosDM)/ATR if ATR > 0 else 0
		negDmiVector[i] = np.mean(cutNegDM)/ATR if ATR > 0 else 0

	posMatrix = [posDmiVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=posDmiVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		posMatrix.append(resamplVector)

	negMatrix = [negDmiVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=negDmiVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		negMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):
		
		real_i = i+1
		multi = volMulti[i]
		window = int(baseWindow*multi) if int(baseWindow*multi) > 2 else 2
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		currentPreCutPositive = posMatrix[address][real_i-window:real_i]
		currentPreCutNegative = negMatrix[address][real_i-window:real_i]
		pastPreCutPositive = posMatrix[address][i-window:i]
		pastPreCutNegative = negMatrix[address][i-window:i]

		currentCutPosDI = concentrator(preCutWindow=currentPreCutPositive, numberMissing=address)
		currentCutNegDI = concentrator(preCutWindow=currentPreCutNegative, numberMissing=address)
		pastCutPosDI = concentrator(preCutWindow=pastPreCutPositive, numberMissing=address)
		pastCutNegDI = concentrator(preCutWindow=pastPreCutNegative, numberMissing=address)

		currentCutDXI = 100*np.abs(currentCutPosDI - currentCutNegDI)/(currentCutPosDI + currentCutNegDI)
		pastCutDXI = 100*np.abs(pastCutPosDI - pastCutNegDI)/(pastCutPosDI + pastCutNegDI)
		
		currentADX = np.mean(currentCutDXI)
		pastADX = np.mean(pastCutDXI)

		adxVector[i] = currentADX
		adxDiffVector[i] = currentADX - pastADX
	
	return posDmiVector, negDmiVector, adxVector, adxDiffVector

@njit(cache=True)
def adaptive_correlation(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int = 20,
		depth: int = 0
	) -> npt.NDArray[np.float64]:

	lenth = len(primaryVector)
	model = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	secondaryMatrix = [secondaryVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=secondaryVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		secondaryMatrix.append(resamplVector)

	primaryMatrix = [primaryVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=primaryVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		primaryMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):

		real_i = i+1
		multi = volMulti[i] if volMulti[i] > 1.0 else 1.0
		window = int(baseWindow*multi)
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		preCutSecondary = secondaryMatrix[address][real_i-window:real_i]
		preCutPrimary = primaryMatrix[address][real_i-window:real_i]

		cutSecondary = concentrator(preCutWindow=preCutSecondary, numberMissing=address)
		cutPrimary = concentrator(preCutWindow=preCutPrimary, numberMissing=address)

		model[i] = lr_correlation(cutPrimary, cutSecondary)
	
	return model

@njit(cache=True)
def simple_correlation(
		secondaryVector: npt.NDArray[np.float64],
		primaryVector: npt.NDArray[np.float64],
		baseWindow: int = 20
	) -> npt.NDArray[np.float64]:

	lenth = len(primaryVector)
	model = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow
	for i in range(firstIndex, lenth):
		real_i = i+1
		window = baseWindow
		cutSecondary = secondaryVector[real_i-window:real_i]
		cutPrimary = primaryVector[real_i-window:real_i]
		model[i] = lr_correlation(cutPrimary, cutSecondary)
	
	return model

@njit(cache=True)
def adaptive_roc(
		closeVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int = 20,
		depth: int = 0
	) -> npt.NDArray[np.float64]:
	lenth = len(closeVector)
	rocVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	closeMatrix = [closeVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=closeVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='end'
		)
		closeMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):
		real_i = i+1
		multi = volMulti[i] if volMulti[i] > 1.0 else 1.0
		window = int(baseWindow*multi)
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		preCutClose = closeMatrix[address][real_i-window:real_i]
		cutClose = concentrator(preCutWindow=preCutClose, numberMissing=address)

		rocVector[i] = (cutClose[-1] - cutClose[0])/cutClose[0]
	
	return rocVector

@njit(cache=True)
def adaptive_volume(
		volumeVector: npt.NDArray[np.float64],
		volMulti: npt.NDArray[np.float64],
		baseWindow: int = 20,
		depth: int = 0
	) -> npt.NDArray[np.float64]:
	lenth = len(volumeVector)
	sumVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*int(np.max(volMulti))

	volumeMatrix = [volumeVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=volumeVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='sum'
		)
		volumeMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):

		real_i = i+1
		multi = volMulti[i] if volMulti[i] > 1.0 else 1.0
		window = int(baseWindow*multi)
		address = int(np.log2(multi)) if (multi < 2**depth) else int(np.log2(2**depth))

		preCutVolume = volumeMatrix[address][real_i-window:real_i]
		cutVolume = concentrator(preCutWindow=preCutVolume, numberMissing=address)
		
		sumVector[i] = np.sum(cutVolume)
	
	return sumVector

#end indicators

#start multi_volativity
@njit(cache=True)
def multi_volativity(
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		baseVolativity: float,
		baseWindow: int = 200,
		depth: int = 0
	) -> npt.NDArray[np.float64]:
	
	lenth = len(highVector)
	volMultiVector = np.empty(lenth, dtype=np.float64)
	firstIndex = baseWindow*(depth+1)
	window = baseWindow

	maxMulti = 2**(depth+1)
	minMulti = 0.5

	highMatrix = [highVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=highVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='max'
		)
		highMatrix.append(resamplVector)

	lowMatrix = [lowVector]
	for i in range(depth):
		relativeTimeFrame = 2**(i+1)
		resamplVector = hotResampler(
			baseVector=lowVector,
			relativeTimeFrame=relativeTimeFrame,
			resamplMode='min'
		)
		lowMatrix.append(resamplVector)

	for i in range(firstIndex, lenth):
		real_i = i+1

		tempVectorValues = np.empty(0, dtype=np.float64)
		for address in range(depth+1):

			preCutHigh = highMatrix[address][real_i-window:real_i]
			preCutLow = lowMatrix[address][real_i-window:real_i]

			cutHigh = concentrator(preCutWindow=preCutHigh, numberMissing=address)
			cutLow = concentrator(preCutWindow=preCutLow, numberMissing=address)

			cutTrueRange = 100*(cutHigh/cutLow - 1)
			localATR = np.mean(cutTrueRange)
			targetATR = localATR*(1/(2**address))**(0.5)

			tempVectorValues = np.append(tempVectorValues, targetATR)

		volMultiVector[i] = baseVolativity/np.mean(tempVectorValues)

	for i in range(len(volMultiVector)):
		value = volMultiVector[i]
		value = value if value < maxMulti else maxMulti
		value = value if value > minMulti else minMulti
		volMultiVector[i] = value

	return volMultiVector
#end multi_volativity
