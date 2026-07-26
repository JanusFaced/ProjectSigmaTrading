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
		fees: float = 0.0005, #0.0005 - FUTURES_TAKER | 0.0002 - FUTURES_MAKER
		leverage: int = 1
	) -> tuple[float, float, float, bool]:

	signal: int = 0
	if (long_signal == -1) and (short_signal == -1):
		signal = -1
	elif (short_signal == 1) and (long_signal == 1):
		signal = 1
	
	tradingEvent = False
	if signal == -1:
		if (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True
		
		if (active == 0) and (fiat > 0):
			active = ((fiat*leverage)/price)*(1-fees)
			fiat -= fiat*leverage
			tradingEvent = True
	
	elif signal == 1:
		if (active > 0) and (fiat <= 0):
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True
		
		if (active == 0) and (fiat > 0):
			active = -(fiat*leverage)/price
			fiat += np.abs(active)*price*(1-fees)
			tradingEvent = True
	
	else:
		if (active > 0) and (fiat <= 0):
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True

		elif (active < 0) and (fiat > 0):
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True

	balance = fiat + active*price

	return fiat, active, balance, tradingEvent