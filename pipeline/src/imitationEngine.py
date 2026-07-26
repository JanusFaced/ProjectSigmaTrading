from numba import njit
import numpy as np
import sys
import os
from logger_setup import get_logger

logger = get_logger(__name__)

def imitationMode(
		price: float,
		long_signal: int,
		short_signal: int,
		fiat: float,
		active: float,
		fees: float = 0.002, #0.002 - SPOT_TAKER | 0.0008 - SPOT_MAKER | 0.0005 - FUTURES_TAKER | 0.0002 - FUTURES_MAKER
		leverage: int = 1
	) -> tuple[float, float, float, bool]:

	if long_signal == -1:
		signal = 'LONG'
	elif short_signal == 1:
		signal = 'SHORT'
	else:
		signal = 'CLOSE'

	tradingEvent = False

	if signal == 'LONG':
		logger.info('Signal is BUY')
		if active > 0:
			logger.info(f'[We in LONG] {fiat} {active}')
		elif active < 0:
			logger.info(f'We in SHORT!!! {fiat} {active}')
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True
			logger.info(f'SHORT is closed! {fiat} {active}')
		
		if active == 0:
			active = ((fiat*leverage)/price)*(1-fees)
			fiat -= fiat*leverage
			logger.info(f'LONG is opened! {fiat} {active}')
	
	elif signal == 'SHORT':
		logger.info('Signal is SELL')
		if active < 0:
			logger.info(f'[We in SHORT] {fiat} {active}')
		elif active > 0:
			logger.info(f'We in LONG!!! {fiat} {active}')
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True
			logger.info(f'LONG is closed! {fiat} {active}')
		
		if active == 0:
			active = -(fiat*leverage)/price
			fiat += np.abs(active)*price*(1-fees)
			logger.info(f'SHORT is opened! {fiat} {active}')
	
	else:
		logger.info('Signal is CLOSE')
		if active > 0:
			logger.info(f'We in LONG!!! {fiat} {active}')
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True
			logger.info(f'LONG is closed! {fiat} {active}')
		elif active < 0:
			logger.info(f'We in SHORT!!! {fiat} {active}')
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True
			logger.info(f'SHORT is closed! {fiat} {active}')

		if active == 0:
			logger.info('We are not in position!')

	balance = fiat + active*price

	return fiat, active, balance, tradingEvent

@njit(cache=True)
def testWork(
		price: float,
		long_signal: int,
		short_signal: int,
		fiat: float,
		active: float,
		fees: float = 0.002, #0.002 - SPOT_TAKER | 0.0008 - SPOT_MAKER | 0.0005 - FUTURES_TAKER | 0.0002 - FUTURES_MAKER
		leverage: int = 1
	) -> tuple[float, float, float, bool]:

	signal: int = 0
	if long_signal == -1:
		signal = -1
	elif short_signal == 1:
		signal = 1
		
	tradingEvent = False
	if signal == -1:
		if active < 0:
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True
		
		if active == 0:
			active = ((fiat*leverage)/price)*(1-fees)
			fiat -= fiat*leverage
	
	elif signal == 1:
		if active > 0:
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True
		
		if active == 0:
			active = -(fiat*leverage)/price
			fiat += np.abs(active)*price*(1-fees)
	
	else:
		if active > 0:
			fiat += active*price*(1-fees)
			active = 0
			tradingEvent = True

		elif active < 0:
			fiat += active*price*(1+fees)
			active = 0
			tradingEvent = True

	balance = fiat + active*price

	return fiat, active, balance, tradingEvent