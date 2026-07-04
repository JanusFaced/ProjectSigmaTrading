from typing import Any, TypedDict, Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ccxt
import sys
import os
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)

def main(inputMessage: dict, dataFrame: pd.DataFrame) -> None:
	
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

	freeFiat, positionActive, balance = imitationConnector(exchange, ticker, signal, freeFiat, positionActive)

def imitationConnector(
		exchange: Any,
		ticker: str,
		signal: int,
		freeFiat: float,
		positionActive: float
	) -> tuple[float, float, float]:

	tickerData = exchange.fetch_ticker(ticker)
	price = tickerData['last']

	fees = 0.001
	leverage = 1

	if signal == -1:
		logger.info('Signal is BUY')
		if positionActive > 0:
			logger.info(f'[We in LONG] {freeFiat} {positionActive}')
		elif positionActive < 0:
			logger.info(f'We in SHORT!!! {freeFiat} {positionActive}')
			freeFiat += positionActive*price*(1+fees)
			positionActive = 0
			logger.info(f'SHORT is closed! {freeFiat} {positionActive}')
		
		if positionActive == 0:
			positionActive = ((freeFiat*leverage)/price)*(1-fees)
			freeFiat -= freeFiat*leverage
			logger.info(f'LONG is opened! {freeFiat} {positionActive}')
	
	elif signal == 1:
		logger.info('Signal is SELL')
		if positionActive < 0:
			logger.info(f'[We in SHORT] {freeFiat} {positionActive}')
		elif positionActive > 0:
			logger.info(f'We in LONG!!! {freeFiat} {positionActive}')
			freeFiat += positionActive*price*(1-fees)
			positionActive = 0
			logger.info(f'LONG is closed! {freeFiat} {positionActive}')
		
		if positionActive == 0:
			positionActive = -(freeFiat*leverage)/price
			freeFiat += np.abs(positionActive)*price*leverage*(1-fees)
			logger.info(f'SHORT is opened! {freeFiat} {positionActive}')
	
	else:
		logger.info('No signals...')

	balance = freeFiat + positionActive*price

	return freeFiat, positionActive, balance

	