from typing import Any, TypedDict, Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ccxt
import sys
import os
from saveToDB import receiveSignals, sendSignals, receiveTrads, sendTrads
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)

def main(inputMessage: dict, dataFrame: pd.DataFrame) -> None:
	
	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	nameStrategy = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"

	if nameExchange == 'binance':
		exchange = ccxt.binance()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'
	
	elif nameExchange == 'bybit':
		exchange = ccxt.bybit()
		if type == 'futures':
			exchange.options['defaultType'] = 'linear'

	elif nameExchange == 'kucoin':
		exchange = ccxt.kucoin()
		if type == 'futures':
			exchange.options['defaultType'] = 'future'

	else:
		raise ValueError(f"Неизвестная биржа: {nameExchange}")

	if type == 'spot':
		ticker: str = f'{symbol}/USDT'
	elif type == 'futures':
		ticker: str = f'{symbol}/USDT:USDT'

	try:
		long_signal = int(dataFrame['long_signal'].iloc[-1])
	except Exception as e:
		logger.info(f'Error long_signal {e}')
		long_signal = 1

	try:
		short_signal = int(dataFrame['short_signal'].iloc[-1])
	except Exception as e:
		logger.info(f'Error short_signal {e}')
		short_signal = -1

	receiveData = receiveSignals(nameStrategy=nameStrategy)

	if receiveData['exist']:
		if receiveData['status'] == 'work':
			fiat = receiveData['fiat']
			active = receiveData['active']
		elif receiveData['status'] == 'new':
			fiat = 100.0
			active = 0.0
			receiveData['status'] = 'work'
	else:
		fiat = 100.0
		active = 0.0
		receiveData['status'] = 'work'

	fiat, active, deposit, tradingEvent = imitationConnector(
		exchange=exchange,
		ticker=ticker,
		long_signal=long_signal,
		short_signal=short_signal,
		fiat=fiat,
		active=active
	)

	sendData = {
		"long_signal": long_signal,
		"short_signal": short_signal,
		"mode": inputMessage['mode'],
		"status": receiveData['status'],
		"fiat": fiat,
		"active": active,
		"deposit": deposit,
		"tradingEvent": tradingEvent
	}

	while True:
		resultWork = sendSignals(nameStrategy=nameStrategy, signalPuck=sendData)
		if resultWork:
			logger.info('sendSignals is good!')
			break

	checkTrads = receiveTrads(nameStrategy=nameStrategy)

	if sendData['tradingEvent'] or checkTrads:
		while True:
			resultWork = sendTrads(nameStrategy=nameStrategy, signalPuck=sendData)
			if resultWork:
				logger.info('sendTrads is good!')
				break

	logger.info(f' >>> nameStrategy: {nameStrategy} -> deposit: {deposit} $ <<< ')

def imitationConnector(
		exchange: Any,
		ticker: str,
		long_signal: int,
		short_signal: int,
		fiat: float,
		active: float
	) -> tuple[float, float, float, bool]:

	if long_signal == -1:
		signal = 'LONG'
	elif short_signal == 1:
		signal = 'SHORT'
	else:
		signal = 'CLOSE'

	tickerData = exchange.fetch_ticker(ticker)
	price = tickerData['last']

	fees = 0.001
	leverage = 1
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
			tradingEvent = True
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
			fiat += np.abs(active)*price*leverage*(1-fees)
			tradingEvent = True
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

	