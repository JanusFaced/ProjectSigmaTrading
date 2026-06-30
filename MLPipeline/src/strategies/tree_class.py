from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
from darts.models import SKLearnClassifierModel
from sklearn.tree import DecisionTreeClassifier
from darts import TimeSeries
from darts import concatenate
from darts.metrics import mape
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

	train_size: int = 1000
	train_step: int = 1000
	future_covariates_cols = ['roc_0', 'roc_1', 'roc_2']

	windowInd0 = 20
	windowInd1 = 50
	windowInd2 = 200
	dataFrame['roc_0'] = dataFrame['close']/dataFrame['close'].shift(windowInd0) - 1
	dataFrame['roc_1'] = dataFrame['close']/dataFrame['close'].shift(windowInd1) - 1
	dataFrame['roc_2'] = dataFrame['close']/dataFrame['close'].shift(windowInd2) - 1

	windowClass0 = 20
	dataFrame['ma'] = dataFrame['close'].rolling(window=windowClass0).mean()
	dataFrame['ma_class'] = dataFrame['ma'].shift(-windowClass0//2)
	dataFrame['ma_class_diff_0'] = dataFrame['ma_class']/dataFrame['ma_class'].shift(1) - 1

	windowClass1 = 200
	dataFrame['ma'] = dataFrame['close'].rolling(window=windowClass1).mean()
	dataFrame['ma_class'] = dataFrame['ma'].shift(-windowClass1//2)
	dataFrame['ma_class_diff_1'] = dataFrame['ma_class']/dataFrame['ma_class'].shift(1) - 1

	
	dataFrame['origin'] = np.select(
		[
			(dataFrame['ma_class_diff_0'] > 0) & (dataFrame['ma_class_diff_1'] > 0),
			(dataFrame['ma_class_diff_0'] < 0) & (dataFrame['ma_class_diff_1'] < 0),
		],
		[2, 0],
		default=1
	)

	cutPoint = max([windowInd0, windowInd1, windowInd2, windowClass0, windowClass1])
	dataFrame = dataFrame.loc[cutPoint:]

	maxWindowClass = max([windowClass0, windowClass1])
	overlap: int = maxWindowClass//2

	seriesOpen = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='open')
	seriesHigh = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='high')
	seriesLow = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='low')
	seriesClose = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='close')
	seriesVolume = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='volume')
	seriesOrigin = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='origin')
	seriesCovariates = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols=future_covariates_cols)

	imageModel = DecisionTreeClassifier(
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        criterion='gini'
    )
	model = SKLearnClassifierModel(
		model=imageModel,
		lags=None,
		lags_future_covariates=[0],
		output_chunk_length=1
	)

	listTestOpen = []
	listTestHigh = []
	listTestLow = []
	listTestClose = []
	listTestVolume = []
	listTestOrigin = []
	listListsForecasts = []

	pastIndex = (len(seriesClose) // train_step)*train_step

	for indexSplit in range(train_step, len(seriesClose), train_step):
		
		trainStart = indexSplit - train_step
		trainEnd = indexSplit

		trainSeriesOrigin = seriesOrigin[trainStart:trainEnd]
		trainSeriesCovariates = seriesCovariates[trainStart:trainEnd]

		model.fit(
			series=trainSeriesOrigin,
			future_covariates=trainSeriesCovariates
		)

		testStart = indexSplit + overlap
		testEnd = indexSplit + train_step + overlap

		if indexSplit == pastIndex:
			testSeriesOpen = seriesOpen[testStart:]
			testSeriesHigh = seriesHigh[testStart:]
			testSeriesLow = seriesLow[testStart:]
			testSeriesClose = seriesClose[testStart:]
			testSeriesVolume = seriesVolume[testStart:]
			testSeriesOrigin = seriesOrigin[testStart:]
			testSeriesCovariates = seriesCovariates[testStart:]

		else:
			testSeriesOpen = seriesOpen[testStart:testEnd]
			testSeriesHigh = seriesHigh[testStart:testEnd]
			testSeriesLow = seriesLow[testStart:testEnd]
			testSeriesClose = seriesClose[testStart:testEnd]
			testSeriesVolume = seriesVolume[testStart:testEnd]
			testSeriesOrigin = seriesOrigin[testStart:testEnd]
			testSeriesCovariates = seriesCovariates[testStart:testEnd]

		historical_forecasts = model.historical_forecasts(
			series=testSeriesOrigin,
			future_covariates=testSeriesCovariates,
			start=0,
			forecast_horizon=1,
			stride=1,
			retrain=False,
			overlap_end=True,
			verbose=True
		)

		listTestOpen.append(testSeriesOpen)
		listTestHigh.append(testSeriesHigh)
		listTestLow.append(testSeriesLow)
		listTestClose.append(testSeriesClose)
		listTestVolume.append(testSeriesVolume)
		listTestOrigin.append(testSeriesOrigin)
		listListsForecasts.append(historical_forecasts)
	
	testSeriesOpen = concatenate(listTestOpen, axis=0)
	testSeriesHigh = concatenate(listTestHigh, axis=0)
	testSeriesLow = concatenate(listTestLow, axis=0)
	testSeriesClose = concatenate(listTestClose, axis=0)
	testSeriesVolume = concatenate(listTestVolume, axis=0)
	testSeriesOrigin = concatenate(listTestOrigin, axis=0)
	forecastValues = concatenate(listListsForecasts, axis=0)

	testDatetime = testSeriesClose.time_index
	testSeriesOpen = testSeriesOpen.values().flatten()
	testSeriesHigh = testSeriesHigh.values().flatten()
	testSeriesLow = testSeriesLow.values().flatten()
	testSeriesClose = testSeriesClose.values().flatten()
	testSeriesVolume = testSeriesVolume.values().flatten()
	testSeriesOrigin = testSeriesOrigin.values().flatten()
	forecastValues = forecastValues.values().flatten()

	min_len = min(
		[
			len(testDatetime),
			len(testSeriesOpen),
			len(testSeriesHigh),
			len(testSeriesLow),
			len(testSeriesClose),
			len(testSeriesVolume),
			len(testSeriesOrigin),
			len(forecastValues)
		]
	)

	testDatetime = testDatetime[:min_len]
	testSeriesOpen = testSeriesOpen[:min_len]
	testSeriesHigh = testSeriesHigh[:min_len]
	testSeriesLow = testSeriesLow[:min_len]
	testSeriesClose = testSeriesClose[:min_len]
	testSeriesVolume = testSeriesVolume[:min_len]
	testSeriesOrigin = testSeriesOrigin[:min_len]
	forecastValues = forecastValues[:min_len]

	dataFrame = pd.DataFrame({
		'datetime': testDatetime,
		'open': testSeriesOpen,
		'high': testSeriesHigh,
		'low': testSeriesLow,
		'close': testSeriesClose,
		'volume': testSeriesVolume,
		'origin': testSeriesOrigin,
		'model': forecastValues,
	})

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['model'] == 2),
			(dataFrame['model'] == 1) & (dataFrame['model'] == 0)
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['model'] == 1) & (dataFrame['model'] == 2),
			(dataFrame['model'] == 0),
		],
		[
			-1,
			1
		],
		default=-1
	)

	#testDF = dataFrame.tail(200)
	#superName = f"{strategy}_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['origin'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]