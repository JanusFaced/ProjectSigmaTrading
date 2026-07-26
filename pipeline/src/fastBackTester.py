import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import imitationEngine
from logger_setup import get_logger

logger = get_logger(__name__)

def main(dataFrame: pl.DataFrame, testMode: str) -> dict:
	testMode = 1 if testMode == 'cumul' else 0

	cash_balance_body, cash_balance_cold, delta_trads, len_trads = backtest(
		openVector = dataFrame['open'].to_numpy(),
		highVector = dataFrame['high'].to_numpy(),
		lowVector = dataFrame['low'].to_numpy(),
		closeVector = dataFrame['close'].to_numpy(),
		volumeVector = dataFrame['volume'].to_numpy(),
		longSignalVector = dataFrame['long_signal'].to_numpy(),
		shortSignalVector = dataFrame['short_signal'].to_numpy(),
		testMode = testMode,
	)

	#trads and freq_trads
	trads = len(delta_trads)
	freq_trads = trads/len(cash_balance_body)

	if trads > 0:
		#win_loss
		posDeltaTrads = delta_trads[delta_trads > 0]
		negDeltaTrads = delta_trads[delta_trads < 0]
		winCount = len(posDeltaTrads)
		lossCount = len(negDeltaTrads)
		win_loss = round(100*winCount/(winCount + lossCount), 2)

		#average_profit_size and max_profit_size
		if winCount > 0:
			average_profit_size = np.mean(posDeltaTrads)
			max_profit_size = np.max(posDeltaTrads)

		else:
			average_profit_size = 0
			max_profit_size = 0

		#average_loss_size and max_loss_size
		if lossCount > 0:
			average_loss_size =  np.mean(negDeltaTrads)
			max_loss_size = np.max(negDeltaTrads)

		else:
			average_loss_size = 0
			max_loss_size = 0

		#max_len_trad and average_len_trad and min_len_trad
		if len(len_trads) > 0:
			max_len_trad = np.max(len_trads)
			average_len_trad = np.mean(len_trads)
			min_len_trad = np.min(len_trads)

		else:
			max_len_trad = 0
			average_len_trad = 0
			min_len_trad = 0

		#amount_profit_signal and amount_loss_signal
		amount_profit_signal = winCount
		amount_loss_signal = lossCount

	else:
		posDeltaTrads = []
		negDeltaTrads = []
		winCount = 0
		lossCount = 0
		win_loss = 0
		average_profit_size = 0
		max_profit_size = 0
		average_loss_size = 0
		max_loss_size = 0
		max_len_trad = 0
		average_len_trad = 0
		min_len_trad = 0
		amount_profit_signal = 0
		amount_loss_signal = 0

	send_list = {
		'trads': trads,
		'freqTrads': freq_trads,
		'balanceBody': cash_balance_body,
		'balanceCold': cash_balance_cold,
		'winrate': win_loss,
		'averageProfitSize': average_profit_size,
		'maxProfitSize': max_profit_size,
		'averageLossSize': average_loss_size,
		'maxLossSize': max_loss_size,
		'maxLengthTrade': max_len_trad,
		'averageLengthTrade': average_len_trad,
		'minLenthTrade': min_len_trad,
		'amountTakeProfit': 0,
		'amountStopLoss': 0,
		'amountProfitSignal': amount_profit_signal,
		'amountLossSignal': amount_loss_signal,
	}

	return send_list

@njit(cache=True)
def backtest(
		openVector: npt.NDArray[np.float64],
		highVector: npt.NDArray[np.float64],
		lowVector: npt.NDArray[np.float64],
		closeVector: npt.NDArray[np.float64],
		volumeVector: npt.NDArray[np.float64],
		longSignalVector: npt.NDArray[np.int64],
		shortSignalVector: npt.NDArray[np.int64],
		testMode: int,
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.int64]]:

	start_fiat: float = 100.0
	leverage: int = 1
	max_lot: float = start_fiat

	lenthDataFrame: int = len(closeVector)
	cash_balance_body: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	cash_balance_cold: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)

	cold_fiat: float = 0.0
	fiat: float = start_fiat
	active: float = 0.0

	delta_trads: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	len_trads: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	oldDeposite: float = start_fiat
	oldTimePoint: int = 0

	for i in range(lenthDataFrame):
		openValue = openVector[i]
		highValue = highVector[i]
		lowValue = lowVector[i]
		closeValue = closeVector[i]
		volumeValue = volumeVector[i]
		longSignal = longSignalVector[i]
		shortSignal = shortSignalVector[i]

		fiat, active, deposit, tradingEvent = imitationEngine.testWork(
			price=closeValue,
			long_signal=longSignal,
			short_signal=shortSignal,
			fiat=fiat,
			active=active,
			leverage = leverage
		)

		if tradingEvent:
			if longSignal == -1 or shortSignal == 1:
				oldDeposite = deposit
				oldTimePoint = i

			elif longSignal == 1 or shortSignal == -1:
				delta_dep = 100*(deposit - oldDeposite)/oldDeposite
				delta_time = i - oldTimePoint

				delta_trads = np.append(delta_trads, delta_dep)
				len_trads = np.append(len_trads, delta_time)

				if testMode == 1:
					if fiat > max_lot:
						cold_fiat += fiat - max_lot
						fiat = max_lot

		cash_balance_body = np.append(cash_balance_body, deposit)
		cash_balance_cold = np.append(cash_balance_cold, cold_fiat)

	return cash_balance_body, cash_balance_cold, delta_trads, len_trads
