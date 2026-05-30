from typing import Any, TypedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
from darts.models import CatBoostModel
from darts import TimeSeries
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import r2_score
import savePredictToDatabase
from dataBaseModels import Session
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> None:

	symbol = inputMessage["symbol"]
	timeFrame = inputMessage["timeFrame"]

	futuresDays = 20
	uniCut = len(dataFrame) - futuresDays

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

	seriesFull = TimeSeries.from_dataframe(
		dataFrame,
		time_col='datetime',
		value_cols='close',
		fill_missing_dates=True,
		freq=timeFrame
	)

	model = CatBoostModel(
		lags=20,
		output_chunk_length=1,
		loss_function='RMSE',
		iterations=500,
		depth=8,
		learning_rate=0.08,
		verbose=False
	)
	model.fit(seriesTrain)

	yDataTest: np.ndarray[np.float64] = np.array(dataFrame['close'])[uniCut:]
	yPredictSeries = model.predict(n=len(yDataTest))

	yPredict: np.ndarray[np.float64] = yPredictSeries.values().flatten()
	mape = mean_absolute_percentage_error(yDataTest, yPredict)
	r2 = r2_score(yDataTest, yPredict)
	logger.info(f"Относительная ошибка: {100*mape:.4f} %")
	logger.info(f"Коэффициент детерминации: {r2:.4f}")

	model.fit(seriesFull)
	yPredictSeries = model.predict(n=futuresDays)
	seriesFull = seriesFull[-futuresDays:]

	seriesFull.plot(label='PastData', color="black")
	yPredictSeries.plot(label='PredictFutureData', color="purple")
	plt.savefig(os.path.join("output/", f"predict_{symbol}_{timeFrame}.png"))
	plt.close()


	try:
		db_session = Session()

		service = savePredictToDatabase.ForecastService(db_session)

		forecast_id = service.save_forecast(
			symbol=symbol,
			timeframe=timeFrame,
			historical_series=seriesFull,
			predicted_series=yPredictSeries,
			mape=mape
		)
		
		logger.info(f"Прогноз сохранён с ID: {forecast_id}")

	except Exception as e:
		logger.error(f"Ошибка сохранения: {e}")
		db_session.rollback()
	finally:
		db_session.close()