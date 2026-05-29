from typing import Any, TypedDict
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import ElasticNet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import r2_score
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> None:

	dataFrame, featuresList = prepareDataFrame(dataFrame=dataFrame)

	quantile = 0.90
	uniCut = int(len(dataFrame)*quantile)

	imageModel = ElasticNet()

	param_grid = {
		'alpha': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100],
		'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
	}

	grid_search = GridSearchCV(
		estimator=imageModel,
		param_grid=param_grid,
		cv=5,
		scoring='neg_root_mean_squared_error',
		n_jobs=-1,
		verbose=1
	)

	yData: NDArray[np.float64] = np.array(dataFrame['futureDiff'])[:uniCut]
	xData: NDArray[NDArray[np.float64]] = dataFrame[featuresList].iloc[:uniCut].to_numpy()
	grid_search.fit(xData, yData)
	logger.info(f"Лучшие параметры: {grid_search.best_params_}")
	logger.info(f"Лучшая ошибка: {round(abs(100*(grid_search.best_score_)), 2)} %")
	model = grid_search.best_estimator_

	yData: NDArray[np.float64] = np.array(dataFrame['futureDiff'])[uniCut:]
	xData: NDArray[NDArray[np.float64]] = dataFrame[featuresList].iloc[uniCut:].to_numpy()
	yPredict: NDArray[np.float64] = model.predict(xData)

	yDataCorrect: NDArray[np.float64] = (yData + 1)*dataFrame['close'][uniCut:]
	yPredictCorrect: NDArray[np.float64] = (yPredict + 1)*dataFrame['close'][uniCut:]

	mape = mean_absolute_percentage_error(yDataCorrect[:-1], yPredictCorrect[:-1])
	r2 = r2_score(yDataCorrect[:-1], yPredictCorrect[:-1])

	logger.info(f"Относительная ошибка: {100*mape:.4f} %")
	logger.info(f"Коэффициент детерминации: {r2:.4f}")

	makeRecursivePredict(
		recusiveXData=xData[-1:],
		model=model,
		symbol=inputMessage['symbol'],
		timeFrame=inputMessage['timeFrame']
	)

def prepareDataFrame(
		dataFrame: pd.DataFrame,
		shifts: list = range(1,20)
	) -> tuple[pd.DataFrame, list]:

	featuresList: list = []
	for shift in shifts:
		name = f'featureShift{shift}'
		featuresList.append(name)
		dataFrame[name] = makeDiff(dataFrameSeries=dataFrame['close'], shift=shift)
	
	dataFrame['futureDiff'] = makeDiff(dataFrameSeries=dataFrame['close'], shift=0)
	
	return dataFrame.iloc[max(shifts):], featuresList

def makeDiff(dataFrameSeries: pd.Series, shift: int = 1) -> pd.Series:
	return dataFrameSeries.shift(shift-1)/dataFrameSeries.shift(shift) - 1

def makeRecursivePredict(
		recusiveXData: NDArray[NDArray[np.float64]],
		model: ElasticNet,
		symbol: str,
		timeFrame: str
	) -> None:

	pastVector: NDArray[np.float64] = recusiveXData[0]
	lenth: int = len(recusiveXData[0])

	for _ in range(lenth):
		yPredict: float = model.predict(recusiveXData)[0]
		workVector: NDArray[np.float64] = recusiveXData[0]
		workVector = np.append(workVector[1:], yPredict)
		recusiveXData = np.array([workVector])

	futureVector: NDArray[np.float64] = recusiveXData[0]
	
	uniteArray = 1 + np.concatenate([pastVector, futureVector])
	result = 100*(np.cumprod(uniteArray))
	time = range(0, lenth*2)

	logger.info(f"result cumprod = \n{result}")

	plt.plot(time[:lenth], result[:lenth])
	plt.plot(time[lenth:], result[lenth:])
	plt.savefig(
		os.path.join("output/", f"predict_{symbol}_{timeFrame}.png"),
	)
	plt.close()