from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit
from darts.models import CatBoostClassifierModel
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
	train_step: int = 1000
	name_origin = 'origin'
	future_covariates_cols = ['roc_0', 'roc_1', 'roc_2']

	windowInd0 = 10 #10
	windowInd1 = 20 #20
	windowInd2 = 30 #30
	windowClass = 30 #30
	futureShift = -windowClass//2

	dataFrame['roc_0'] = dataFrame['close']/dataFrame['close'].shift(windowInd0) - 1
	dataFrame['roc_1'] = dataFrame['close']/dataFrame['close'].shift(windowInd1) - 1
	dataFrame['roc_2'] = dataFrame['close']/dataFrame['close'].shift(windowInd2) - 1

	dataFrame['ma'] = dataFrame['close'].rolling(window=windowClass).mean()
	dataFrame['ma_class'] = dataFrame['ma'].shift(futureShift)
	dataFrame['ma_class_diff'] = dataFrame['ma_class']/dataFrame['ma_class'].shift(1) - 1
	dataFrame['origin'] = np.select([dataFrame['ma_class_diff']>0, dataFrame['ma_class_diff']<0], [1,0], default=1)

	cutPoint = max([windowInd0, windowInd1, windowInd2, windowClass])
	dataFrame = dataFrame.loc[cutPoint:]

	seriesOpen = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='open')
	seriesHigh = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='high')
	seriesLow = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='low')
	seriesClose = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='close')
	seriesVolume = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='volume')
	seriesOrigin = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols='origin')
	seriesCovariates = TimeSeries.from_dataframe(dataFrame, time_col='datetime', value_cols=future_covariates_cols)

	trainSeriesOpen, testSeriesOpen = seriesOpen[:train_size], seriesOpen[train_size:]
	trainSeriesHigh, testSeriesHigh = seriesHigh[:train_size], seriesHigh[train_size:]
	trainSeriesLow, testSeriesLow = seriesLow[:train_size], seriesLow[train_size:]
	trainSeriesClose, testSeriesClose = seriesClose[:train_size], seriesClose[train_size:]
	trainSeriesVolume, testSeriesVolume = seriesVolume[:train_size], seriesVolume[train_size:]
	trainSeriesOrigin, testSeriesOrigin = seriesOrigin[:train_size], seriesOrigin[train_size:]
	trainSeriesCovariates, testSeriesCovariates = seriesCovariates[:train_size], seriesCovariates[train_size:]

	model = CatBoostClassifierModel(
		lags=None,                            # Лаги целевой переменной
		lags_future_covariates=[0],           # Текущее значение ковариат
		output_chunk_length=1,                # Прогнозируем 1 шаг
		random_state=42,                      # Для воспроизводимости
		iterations=100,                       # Количество деревьев (аналог n_estimators)
		depth=6,                              # Глубина деревьев
		learning_rate=0.1,                    # Скорость обучения
		l2_leaf_reg=3,                        # L2 регуляризация
		border_count=254,                     # Количество разбиений для числовых признаков
		verbose=100,                          # Логирование каждые 100 итераций
	)
	model.fit(
		series=trainSeriesOrigin,
		future_covariates=trainSeriesCovariates
	)

	def logicRetrain(counter, pred_time, train_series, past_covariates, future_covariates):
		return counter % train_step == 0

	historical_forecasts = model.historical_forecasts(
		series=seriesOrigin,
		future_covariates=seriesCovariates,
		start=train_size,
		forecast_horizon=1,
		stride=1,
		train_length=train_size,
		retrain=logicRetrain,
		overlap_end=True,
		verbose=True
	)

	testDatetime = testSeriesClose.time_index
	testSeriesOpen = testSeriesOpen.values().flatten()
	testSeriesHigh = testSeriesHigh.values().flatten()
	testSeriesLow = testSeriesLow.values().flatten()
	testSeriesClose = testSeriesClose.values().flatten()
	testSeriesVolume = testSeriesVolume.values().flatten()
	testSeriesOrigin = testSeriesOrigin.values().flatten()
	forecastValues = historical_forecasts.values().flatten()

	min_len = min(len(historical_forecasts), len(testSeriesClose))
	
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
			(dataFrame['model'] == 1),
			(dataFrame['model'] == 0)
		],
		[
			-1,
			1
		],
		default=1
	)

	dataFrame['short_signal'] = np.select(
		[
			(dataFrame['model'] == 1),
			(dataFrame['model'] == 0)
		],
		[
			-1,
			1
		],
		default=-1
	)

	#testDF = dataFrame.tail(50)
	#superName = f"{strategy}_{nameExchange}_{symbol}_{type}_{timeFrame}.png"
	#plt.plot(testDF['datetime'], testDF['origin'], color="black")
	#plt.plot(testDF['datetime'], testDF['model'], color="purple")
	#plt.savefig(str(output_dir / superName ))
	#plt.close()

	return dataFrame[['datetime', 'open', 'high', 'low', 'close', 'volume', 'long_signal', 'short_signal']]