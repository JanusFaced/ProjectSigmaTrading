from numba import njit
import numpy as np
import sys
import os
from logger_setup import get_logger

logger = get_logger(__name__)

@njit(cache=True)
def coreEngine(
		price: float,
		long_signal: int,
		short_signal: int,
		maxProfit: float,
		maxLoss: float,
		currentPosition: float,
		fiat: float,
		active: float,
		cold_fiat: float = 0.0,
		max_lot: float = False,
		fees: float = 0.0002, #0.0005 - FUTURES_TAKER | 0.0002 - FUTURES_MAKER
		leverage: int = 1,
	) -> tuple[float, float, float, float, dict, float]:

	signal: str = 'WAIT'
	if (long_signal == -1) and (short_signal in [-1, 0]):
		signal = 'LONG'
	elif (short_signal == 1) and (long_signal in [1, 0]):
		signal = 'SHORT'
	elif (long_signal == 1) or (short_signal == -1):
		signal = 'CLOSE:SIGNAL'

	#if active != 0:
	#	currentDeposite = fiat + active*price
	#	currentFinancialReturn = currentDeposite/currentPosition - 1
	#	if (currentFinancialReturn > maxProfit) or (maxLoss > currentFinancialReturn):
	#		long_signal, short_signal = 1, -1
	#		signal = 'CLOSE:STOP'

	tradEvent = {
		'close_long_signal': False,
		'close_long_stop': False,
		'open_long': False,
		'close_short_signal': False,
		'close_short_stop': False,
		'open_short': False
	}

	if signal == 'LONG':
		if (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0
			tradEvent['close_short_signal'] = True
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot
		
		if (active == 0) and (fiat > 0):
			active = ((fiat*leverage)/price)*(1-fees)
			fiat -= fiat*leverage
			tradEvent['open_long'] = True
	
	elif signal == 'SHORT':
		if (active > 0) and (fiat <= 0):
			fiat += active*price*(1-fees)
			active = 0
			tradEvent['close_long_signal'] = True
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot
		
		if (active == 0) and (fiat > 0):
			active = -(fiat*leverage)/price
			fiat += np.abs(active)*price*(1-fees)
			tradEvent['open_short'] = True
	
	elif signal in ['CLOSE:SIGNAL', 'CLOSE:STOP']:
		if (active > 0) and (fiat <= 0):
			fiat += active*price*(1-fees)
			active = 0
			
			if signal == 'CLOSE:SIGNAL':
				tradEvent['close_long_signal'] = True
			elif signal == 'CLOSE:STOP':
				tradEvent['close_long_stop'] = True
			
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot

		if (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0

			if signal == 'CLOSE:SIGNAL':
				tradEvent['close_short_signal'] = True
			elif signal == 'CLOSE:STOP':
				tradEvent['close_short_stop'] = True

			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot

	balance = fiat + active*price
	financeReturn = balance/currentPosition - 1

	return fiat, active, balance, financeReturn, tradEvent, cold_fiat