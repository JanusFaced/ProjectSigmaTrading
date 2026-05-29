from typing import Any, TypedDict
import pandas as pd
import numpy as np
import os
import sys
from sklearn.metrics import accuracy_score
import catboost as cb
from dataBaseModels import Session, Signal
from logger_setup import get_logger

logger = get_logger(__name__)

class SignalDict(TypedDict):
	asset: str
	ml_model: str
	timeframe: str
	signal: str
	accuracy: str

def main(inputMessage: dict[str, Any], dataFrame: pd.DataFrame) -> None:

	dataFrame, featuresList = prepareDataFrame(dataFrame=dataFrame)

	quantile = 0.90
	uniCut = int(len(dataFrame)*quantile)

	model = cb.CatBoostClassifier(
		iterations=50,
		learning_rate=0.1,
		depth=4,
		loss_function='Logloss',
		random_seed=42,
		verbose=False
	)

	yData = np.array(dataFrame['classEDU'])[:uniCut]
	xData = dataFrame[featuresList].iloc[:uniCut].to_numpy()
	model.fit(xData, yData)

	importance = model.feature_importances_
	for i in range(len(importance)):
		logger.info(f"Важность фичи номер {i}: > {importance[i]:.2f} % <")

	yData = np.array(dataFrame['classEDU'])[uniCut:]
	xData = dataFrame[featuresList].iloc[uniCut:].to_numpy()
	yPredict = model.predict(xData)

	accuracy = accuracy_score(yData, yPredict)
	logger.info(f"Точность модели на Test: {100*accuracy:.2f} %")

	tradingSignal = {0: "long", 1: "short"}.get(yPredict[-1], "neutral")
	
	signalData: SignalDict = {
		"asset": inputMessage['symbol'],
		"ml_model": "CatBoostClass",
		"timeframe": inputMessage['timeFrame'],
		"signal": tradingSignal,
		"accuracy": f"{100*accuracy:.2f} %",
	}

	sendToDataBase(signalData=signalData)

	logger.info(f"sendToDataBase is ended succesfull!")

def prepareDataFrame(
		dataFrame: pd.DataFrame,
		windows: list = [5, 10, 15],
		centreWindow: int = 20
	) -> tuple[pd.DataFrame, list]:

	featuresList: list = []
	for i, window in enumerate(windows):
		name = f'features{i}'
		featuresList.append(name)
		dataFrame[name] = makeFeatures(dataFrame['close'], window)
	
	dataFrame['classEDU'] = makeClass(dataFrame['close'], centreWindow)
	
	return dataFrame.iloc[max(windows):], featuresList

def makeFeatures(dataFrameSeries: pd.Series, windowFeatures: int) -> pd.Series:
	return dataFrameSeries/dataFrameSeries.shift(windowFeatures) - 1

def makeClass(dataFrameSeries: pd.Series, windowFeatures: int) -> pd.Series:
	centreMoving = dataFrameSeries.rolling(window=windowFeatures).mean().shift(-windowFeatures//2)
	diff = centreMoving.diff()
	return (diff < 0).astype(int)

def sendToDataBase(signalData: SignalDict) -> None:
	dataBaseSession = Session()

	try:
		dataBaseSession.query(Signal).filter(
			Signal.asset == signalData['asset'],
			Signal.timeframe == signalData['timeframe']
		).delete()
		
		newSignal = Signal(
			asset=signalData['asset'],
			ml_model=signalData['ml_model'],
			timeframe=signalData['timeframe'],
			signal=signalData['signal'],
			accuracy=signalData['accuracy'],
		)
		dataBaseSession.add(newSignal)
		dataBaseSession.commit()
		
		logger.info(f"Saved {signalData['asset']} {signalData['timeframe']} -> {signalData['signal']} with id={newSignal.id}")
		
	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
	
	finally:
		dataBaseSession.close()