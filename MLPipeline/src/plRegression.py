from typing import Any, TypedDict
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
from darts.models import CatBoostModel
from darts.metrics import smape
from darts import TimeSeries
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import r2_score
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> None:

	symbol = inputMessage["symbol"]
	timeFrame = inputMessage["timeFrame"]

	amountCandles = 10
	uniCut = len(dataFrame) - amountCandles

	dataFrameTrain: pd.DataFrame = dataFrame[:uniCut]
	dataFrameTest: pd.DataFrame = dataFrame[uniCut:]

	seriesTrain = TimeSeries.from_dataframe(
		dataFrameTrain,
		time_col='datetime',
		value_cols='close',
		fill_missing_dates=True,
		freq=timeFrame
	)

	seriesTest = TimeSeries.from_dataframe(
		dataFrameTest,
		time_col='datetime',
		value_cols='close',
		fill_missing_dates=True,
		freq=timeFrame
	)

	param_grid = {
		'lags': [5, 15],
		'iterations': [200, 600],
		'depth': [4, 8],
		'learning_rate': [0.02, 0.08]
	}

	imageModel = CatBoostModel(
		lags=5,
		output_chunk_length=1,
		loss_function='RMSE',
		iterations=200,
		depth=4,
		learning_rate=0.02,
		verbose=False
	)

	model, best_params, best_score = imageModel.gridsearch(
		parameters=param_grid,
		series=seriesTrain,
		val_series=seriesTest,
		metric=smape,
		verbose=True
	)

	logger.info(f"Best parametrs: {best_params}")

	model.fit(seriesTrain)

	yDataTest: NDArray[np.float64] = np.array(dataFrame['close'])[uniCut:]

	yPredictSeries = model.predict(n=len(yDataTest))

	yPredict: NDArray[np.float64] = yPredictSeries.values().flatten()
	mape = mean_absolute_percentage_error(yDataTest, yPredict)
	r2 = r2_score(yDataTest, yPredict)
	logger.info(f"Относительная ошибка: {100*mape:.4f} %")
	logger.info(f"Коэффициент детерминации: {r2:.4f}")

	seriesTrain = seriesTrain[-amountCandles:]

	seriesTrain.plot(label='PastData', color="black")
	seriesTest.plot(label='RealFutureData', color="blue")
	yPredictSeries.plot(label='PredictFutureData', color="purple")
	plt.savefig(os.path.join("output/", f"predict_{symbol}_{timeFrame}.png"))
	plt.close()