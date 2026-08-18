import matplotlib.pyplot as plt
import time
import polars as pl
import numpy as np
import numpy.typing as npt
from numba import njit
import imitationEngine
from logger_setup import get_logger

logger = get_logger(__name__)

def preAnalyst(
		lenthDF: int,
		delta_trads_signal: npt.NDArray[np.float64],
		delta_trads_stop: npt.NDArray[np.float64],
		len_trads: npt.NDArray[np.float64],
	) -> dict:

	amountTakeProfit = len(delta_trads_stop[delta_trads_stop > 0])
	amountStopLoss = len(delta_trads_stop[delta_trads_stop < 0])
	amountProfitSignal = len(delta_trads_signal[delta_trads_signal > 0])
	amountLossSignal = len(delta_trads_signal[delta_trads_signal < 0])

	delta_trads = np.concatenate([delta_trads_signal, delta_trads_stop])

	if len(delta_trads) > 0:
		#trads and freq_trads
		trads = len(delta_trads)
		freq_trads = int(lenthDF/trads)

		#win_loss
		posDeltaTrads = delta_trads[delta_trads > 0]
		negDeltaTrads = delta_trads[delta_trads < 0]
		winCount = len(posDeltaTrads)
		lossCount = len(negDeltaTrads)

		if winCount > 0 or lossCount > 0:
			win_loss = round(100*winCount/(winCount + lossCount), 2)
		else:
			win_loss = 0.00

		#average_profit_size and max_profit_size
		if winCount > 0:
			average_profit_size = 100*round(np.mean(posDeltaTrads), 2)
			max_profit_size = 100*round(np.max(posDeltaTrads), 2)

		else:
			average_profit_size = 0
			max_profit_size = 0

		#average_loss_size and max_loss_size
		if lossCount > 0:
			average_loss_size =  100*round(np.mean(negDeltaTrads), 2)
			max_loss_size = 100*round(np.min(negDeltaTrads), 2)

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

	else:
		trads = 0
		freq_trads = lenthDF
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

	send_list = {
		'trads': trads,
		'freqTrads': freq_trads,
		'winrate': win_loss,
		'averageProfitSize': average_profit_size,
		'maxProfitSize': max_profit_size,
		'averageLossSize': average_loss_size,
		'maxLossSize': max_loss_size,
		'maxLengthTrade': max_len_trad,
		'averageLengthTrade': average_len_trad,
		'minLenthTrade': min_len_trad,
		'amountTakeProfit': amountTakeProfit,
		'amountStopLoss': amountStopLoss,
		'amountProfitSignal': amountProfitSignal,
		'amountLossSignal': amountLossSignal,
	}

	return send_list

def coreBacktester(dataFrame: pl.DataFrame, testMode: str) -> dict:
	testMode = 1 if testMode == 'cumul' else 0

	cash_balance_body, cash_balance_cold, longDeltaTradsSignal, longDeltaTradsStop, longLenTrads, shortDeltaTradsSignal, shortDeltaTradsStop, shortLenTrads = backtest(
		openVector = dataFrame['open'].to_numpy(),
		highVector = dataFrame['high'].to_numpy(),
		lowVector = dataFrame['low'].to_numpy(),
		closeVector = dataFrame['close'].to_numpy(),
		volumeVector = dataFrame['volume'].to_numpy(),
		longSignalVector = dataFrame['long_signal'].to_numpy(),
		shortSignalVector = dataFrame['short_signal'].to_numpy(),
		leverageVector = dataFrame['leverage'].to_numpy(),
		maxLossVector = dataFrame['maxLoss'].to_numpy(),
		maxProfitVector = dataFrame['maxProfit'].to_numpy(),
		testMode = testMode,
	)

	delta_trads_signal = np.concatenate([longDeltaTradsSignal, shortDeltaTradsSignal])
	delta_trads_stop = np.concatenate([longDeltaTradsStop, shortDeltaTradsStop])
	len_trads = np.concatenate([longLenTrads, shortLenTrads])

	lenthDF = len(cash_balance_body)
	general_list = preAnalyst(lenthDF, delta_trads_signal, delta_trads_stop, len_trads)
	long_list = preAnalyst(lenthDF, longDeltaTradsSignal, longDeltaTradsStop, longLenTrads)
	short_list = preAnalyst(lenthDF, shortDeltaTradsSignal, shortDeltaTradsSignal, shortLenTrads)

	send_list = {
		'balanceBody': cash_balance_body,
		'balanceCold': cash_balance_cold,
		'general': general_list,
		'long': long_list,
		'short': short_list,
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
		leverageVector: npt.NDArray[np.int64],
		maxLossVector: npt.NDArray[np.float64],
		maxProfitVector: npt.NDArray[np.float64],
		testMode: int,
	) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.int64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.int64]]:

	lenthDataFrame: int = len(closeVector)

	cash_balance_body: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	cash_balance_cold: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)

	longDeltaTradsSignal: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	longDeltaTradsStop: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	longLenTrads: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	
	shortDeltaTradsSignal: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	shortDeltaTradsStop: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)
	shortLenTrads: npt.NDArray[np.float64] = np.empty(0, dtype=np.float64)

	start_fiat: float = 100.0
	max_lot: float = start_fiat if testMode == 1 else False
	cold_fiat: float = 0.0
	fiat: float = start_fiat
	active: float = 0.0
	currentPosition = start_fiat
	oldTimePoint: int = 0
	tempMaxProfit, tempMaxLoss = maxProfitVector[0], maxLossVector[0]

	for i in range(lenthDataFrame):
		openValue = openVector[i]
		highValue = highVector[i]
		lowValue = lowVector[i]
		closeValue = closeVector[i]
		volumeValue = volumeVector[i]
		longSignal = longSignalVector[i]
		shortSignal = shortSignalVector[i]
		leverage = leverageVector[i]
		maxLoss = maxLossVector[i]
		maxProfit = maxProfitVector[i]

		fiat, active, deposit, financeReturn, tradEvent, cold_fiat = imitationEngine.coreEngine(
			price=closeValue,
			long_signal=longSignal,
			short_signal=shortSignal,
			maxProfit=tempMaxProfit,
			maxLoss=tempMaxLoss,
			currentPosition=currentPosition,
			fiat=fiat,
			active=active,
			cold_fiat=cold_fiat,
			max_lot=max_lot,
			leverage=leverage,
		)

		if tradEvent['close_long_signal'] or tradEvent['close_long_stop']:
			longLenTrads = np.append(longLenTrads, i - oldTimePoint)

			if tradEvent['close_long_signal']:
				longDeltaTradsSignal = np.append(longDeltaTradsSignal, financeReturn)
			
			elif tradEvent['close_long_stop']:
				longDeltaTradsStop = np.append(longDeltaTradsStop, financeReturn)

		elif tradEvent['close_short_signal'] or tradEvent['close_short_stop']:
			shortLenTrads = np.append(shortLenTrads, i - oldTimePoint)

			if tradEvent['close_short_signal']:
				shortDeltaTradsSignal = np.append(shortDeltaTradsSignal, financeReturn)
			
			elif tradEvent['close_short_stop']:
				shortDeltaTradsStop = np.append(shortDeltaTradsStop, financeReturn)

		if tradEvent['open_long'] or tradEvent['open_short']:
			currentPosition = deposit
			tempMaxLoss, tempMaxProfit = maxLoss, maxProfit
			oldTimePoint = i

		#if True in [tradEvent['close_long'], tradEvent['open_long'], tradEvent['close_short'], tradEvent['open_short']]:
		#	if active < 0:
		#		logger.info(f"tradEvent={tradEvent}")
		#		logger.info(f"currentPosition={currentPosition} signalClose={signalClose}")
		#		logger.info(f"open={openValue} high={highValue} low={lowValue} close={closeValue} volume={volumeValue}")
		#		logger.info(f"longSignal={longSignal} shortSignal={shortSignal}")
		#		logger.info(f"fiat={fiat} active={active} deposit={deposit}")
		#		logger.info(f"maxLoss={maxLoss} maxProfit={maxProfit}")
		#		logger.info(f"========================================")
		#	
		#		for _ in range(10): time.sleep(1)

		cash_balance_body = np.append(cash_balance_body, deposit)
		cash_balance_cold = np.append(cash_balance_cold, cold_fiat)

	return cash_balance_body, cash_balance_cold, longDeltaTradsSignal, longDeltaTradsStop, longLenTrads, shortDeltaTradsSignal, shortDeltaTradsStop, shortLenTrads
