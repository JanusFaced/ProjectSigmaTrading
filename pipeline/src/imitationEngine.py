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
		fiat: float,
		active: float,
		cold_fiat: float = 0.0,
		max_lot: float = False,
		fees: float = 0.0002, #0.0005 - FUTURES_TAKER | 0.0002 - FUTURES_MAKER
		leverage: int = 1,
	) -> tuple[float, float, float, list]:

	signal: str = 'WAIT'
	if (long_signal == -1) and (short_signal == -1):
		signal = 'LONG'
	elif (short_signal == 1) and (long_signal == 1):
		signal = 'SHORT'
	
	tradEvent = {
		'close_long': False,
		'open_long': False,
		'close_short': False,
		'open_short': False
	}

	if signal == 'LONG':
		if (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0
			tradEvent['close_short'] = True
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
			tradEvent['close_long'] = True
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot
		
		if (active == 0) and (fiat > 0):
			active = -(fiat*leverage)/price
			fiat += np.abs(active)*price*(1-fees)
			tradEvent['open_short'] = True
	
	else:
		if (active > 0) and (fiat <= 0):
			fiat += active*price*(1-fees)
			active = 0
			tradEvent['close_long'] = True
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot

		elif (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0
			tradEvent['close_short'] = True
			if max_lot and (fiat > max_lot):
				cold_fiat += fiat - max_lot
				fiat = max_lot

	balance = fiat + active*price

	return fiat, active, balance, tradEvent, cold_fiat