from typing import Any, TypedDict
from numpy.typing import NDArray
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
from statsmodels.tsa.arima.model import ARIMA
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

	yDataEdu: NDArray[np.float64] = np.array(dataFrame['close'])[:uniCut]

	imageModel = ARIMA(yDataEdu, order=(10, 1, 1))
	model = imageModel.fit()

	yDataTest: NDArray[np.float64] = np.array(dataFrame['close'])[uniCut:]

	yPredict = model.forecast(steps=len(yDataTest))
	print(f"Прогноз следующих значений: {yPredict}")


	mape = mean_absolute_percentage_error(yDataTest, yPredict)
	r2 = r2_score(yDataTest, yPredict)

	logger.info(f"Относительная ошибка: {100*mape:.4f} %")
	logger.info(f"Коэффициент детерминации: {r2:.4f}")

	yDataEdu = yDataEdu[-amountCandles:]

	lenth = len(yDataEdu)
	time = range(len(yDataEdu) + len(yDataTest))

	plt.plot(time[:lenth], yDataEdu, color="black")
	plt.plot(time[lenth:], yDataTest, color="blue")
	plt.plot(time[lenth:], yPredict, color="purple")
	plt.savefig(
		os.path.join("output/", f"predict_{symbol}_{timeFrame}.png"),
	)
	plt.close()