from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
from darts.models import LinearRegressionModel
from darts import TimeSeries
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

	windowInd = 1
	dataFrame['original'] = dataFrame['close']/dataFrame['close'].shift(windowInd) - 1
	dataFrame['indicator'] = np.abs(dataFrame['original'])

	dataFrame = dataFrame.loc[windowInd:]

	seriesOpen = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='open')
	seriesHigh = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='high')
	seriesLow = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='low')
	seriesClose = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='close')
	seriesVolume = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='volume')
	seriesOriginal = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='original')
	seriesIndicator = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='indicator')

	trainSeriesOpen, testSeriesOpen = seriesOpen[:train_size], seriesOpen[train_size:]
	trainSeriesHigh, testSeriesHigh = seriesHigh[:train_size], seriesHigh[train_size:]
	trainSeriesLow, testSeriesLow = seriesLow[:train_size], seriesLow[train_size:]
	trainSeriesClose, testSeriesClose = seriesClose[:train_size], seriesClose[train_size:]
	trainSeriesVolume, testSeriesVolume = seriesVolume[:train_size], seriesVolume[train_size:]
	trainSeriesOriginal, testSeriesOriginal = seriesOriginal[:train_size], seriesOriginal[train_size:]
	trainSeriesIndicator, testSeriesIndicator = seriesIndicator[:train_size], seriesIndicator[train_size:]

	model = LinearRegressionModel(
		lags=None,
		lags_future_covariates=[0],
		fit_intercept=True
	)
	model.fit(
		series=trainSeriesIndicator,
		future_covariates=trainSeriesVolume
	)

	historical_forecasts = model.historical_forecasts(
		series=seriesIndicator,
		future_covariates=seriesVolume,
		start=train_size,
		forecast_horizon=1,
		stride=1,
		train_length=train_size,
		retrain=True,
		overlap_end=True,
		verbose=True
	)

	testDatetime = testSeriesClose.time_index
	testSeriesOpen = testSeriesOpen.values().flatten()
	testSeriesHigh = testSeriesHigh.values().flatten()
	testSeriesLow = testSeriesLow.values().flatten()
	testSeriesClose = testSeriesClose.values().flatten()
	testSeriesVolume = testSeriesVolume.values().flatten()
	forecastValues = historical_forecasts.values().flatten()
	testSeriesOriginal = testSeriesOriginal.values().flatten()
	testSeriesIndicator = testSeriesIndicator.values().flatten()

	min_len = min(len(historical_forecasts), len(testSeriesIndicator))
	
	testDatetime = testDatetime[:min_len]
	testSeriesOpen = testSeriesOpen[:min_len]
	testSeriesHigh = testSeriesHigh[:min_len]
	testSeriesLow = testSeriesLow[:min_len]
	testSeriesClose = testSeriesClose[:min_len]
	testSeriesVolume = testSeriesVolume[:min_len]
	forecastValues = forecastValues[:min_len]
	testSeriesOriginal = testSeriesOriginal[:min_len]
	testSeriesIndicator = testSeriesIndicator[:min_len]

	dataFrame = pd.DataFrame({
		'datetime': testDatetime,
		'open': testSeriesOpen,
		'high': testSeriesHigh,
		'low': testSeriesLow,
		'close': testSeriesClose,
		'volume': testSeriesVolume,
		'model': forecastValues,
		'original': testSeriesOriginal,
		'indicator': testSeriesIndicator
	})

	dataFrame['long_signal'] = np.select(
		[
			(dataFrame['original'] > dataFrame['model']),
			(dataFrame['original'] < dataFrame['model'])
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['original'] > -dataFrame['model']),
			(dataFrame['original'] < -dataFrame['model'])
		],
		[
			-1,
			1
		],
		default=-1
	)

	#testDF = dataFrame.tail(50)
	#superName = f"{strategy}_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['original'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="green")
	#plt.plot(testDF['datetime'], -testDF['model'], color="red")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]