from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
from darts.models import RandomForest
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

	train_ratio: float = 0.50
	future_covariates_cols = ['open', 'high', 'low', 'close', 'volume']

	windowInd = 20
	dataFrame['indicator'] = dataFrame['close'].rolling(window=windowInd).mean()

	dataFrame = dataFrame.loc[windowInd:]

	seriesOpen = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='open')
	seriesHigh = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='high')
	seriesLow = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='low')
	seriesClose = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='close')
	seriesVolume = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='volume')
	seriesIndicator = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='indicator')
	seriesCovariates = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols=future_covariates_cols)

	train_size = int(len(seriesClose)*train_ratio)

	trainSeriesOpen, testSeriesOpen = seriesOpen[:train_size], seriesOpen[train_size:]
	trainSeriesHigh, testSeriesHigh = seriesHigh[:train_size], seriesHigh[train_size:]
	trainSeriesLow, testSeriesLow = seriesLow[:train_size], seriesLow[train_size:]
	trainSeriesClose, testSeriesClose = seriesClose[:train_size], seriesClose[train_size:]
	trainSeriesVolume, testSeriesVolume = seriesVolume[:train_size], seriesVolume[train_size:]
	trainSeriesIndicator, testSeriesIndicator = seriesIndicator[:train_size], seriesIndicator[train_size:]
	trainSeriesCovariates, testSeriesCovariates = seriesCovariates[:train_size], seriesCovariates[train_size:]

	model = RandomForest(
		lags=None,
		lags_future_covariates=[0],
		n_estimators=100,
		max_depth=10,
		min_samples_split=5,
		min_samples_leaf=2,
		random_state=42,
		n_jobs=-1
	)
	model.fit(
		series=trainSeriesIndicator,
		future_covariates=trainSeriesCovariates
	)

	historical_forecasts = model.historical_forecasts(
		series=testSeriesIndicator,
		future_covariates=testSeriesCovariates,
		start=0,
		forecast_horizon=1,
		stride=1,
		retrain=False,
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
	testSeriesIndicator = testSeriesIndicator.values().flatten()

	min_len = min(len(historical_forecasts), len(testSeriesIndicator))
	
	testDatetime = testDatetime[:min_len]
	testSeriesOpen = testSeriesOpen[:min_len]
	testSeriesHigh = testSeriesHigh[:min_len]
	testSeriesLow = testSeriesLow[:min_len]
	testSeriesClose = testSeriesClose[:min_len]
	testSeriesVolume = testSeriesVolume[:min_len]
	forecastValues = forecastValues[:min_len]
	testSeriesIndicator = testSeriesIndicator[:min_len]

	dataFrame = pd.DataFrame({
		'datetime': testDatetime,
		'open': testSeriesOpen,
		'high': testSeriesHigh,
		'low': testSeriesLow,
		'close': testSeriesClose,
		'volume': testSeriesVolume,
		'model': forecastValues,
		'original': testSeriesIndicator 
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
			(dataFrame['original'] > dataFrame['model']),
			(dataFrame['original'] < dataFrame['model'])
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
	#plt.plot(testDF['datetime'], testDF['model'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]