from typing import Any, TypedDict, Dict
import numpy as np
import ccxt
import os
import imitationEngine
from saveToDB import receiveSignals, sendSignals, sendTrads, sendAdjTrads
from duckDB_setup import get_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict) -> None:
	
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

	long_signal, short_signal, leverage, solidMaxLoss, stepMaxLoss = get_signals()

	receiveData = receiveSignals(nameStrategy=nameStrategy)

	if receiveData['exist']:
		fiat = receiveData['fiat']
		active = receiveData['active']
		stop_loss = receiveData['stop_loss']
		weight_portfolio = receiveData['weight_portfolio']
		current_position = receiveData['current_position']

		tickerData = exchange.fetch_ticker(ticker)
		price = tickerData['last']

		cold_fiat = 0
		max_lot = False

		fiat, active, deposit, financeReturn, tradingEvent, cold_fiat, stop_loss = imitationEngine.coreEngine(
			price=price,
			long_signal=long_signal,
			short_signal=short_signal,
			stepMaxLoss=stepMaxLoss,
			solidMaxLoss=solidMaxLoss,
			tempMaxLoss=stop_loss,
			currentPosition=current_position,
			fiat=fiat,
			active=active,
			cold_fiat=cold_fiat,
			max_lot=max_lot,
			leverage=leverage,
		)

		if tradingEvent['open_long'] or tradingEvent['open_short']:
			current_position = deposit
			stop_loss = solidMaxLoss

		adj_deposite = deposit/weight_portfolio

		sendData = {
			"long_signal": long_signal,
			"short_signal": short_signal,
			"mode": inputMessage['mode'],
			"status": receiveData['status'],
			"fiat": fiat,
			"active": active,
			"deposit": deposit,
			"tradingEvent": tradingEvent,
			"weight_portfolio": weight_portfolio,
			"stop_loss": stop_loss,
			"adj_deposite": adj_deposite,
			"current_position": current_position,
		}

		sendSignals(nameStrategy=nameStrategy, signalPuck=sendData)

		if (
				tradingEvent['close_long_signal'] or
				tradingEvent['close_long_stop'] or
				tradingEvent['close_short_signal'] or
				tradingEvent['close_short_stop']
			):

			sendTrads(nameStrategy=nameStrategy, signalPuck=sendData)
			sendAdjTrads(nameStrategy=nameStrategy, signalPuck=sendData)

		logger.info(f' >>> nameStrategy: {nameStrategy} -> deposit: {deposit} $ <<< ')

	else:
		logger.info(f' --- nameStrategy: {nameStrategy} is not made! --- ')

def get_signals():
	db = get_duckdb()
	
	try:
		result = db.execute("""
			SELECT long_signal, short_signal, leverage, maxLoss, stepMaxLoss
			FROM temp_trading 
			ORDER BY datetime DESC 
			LIMIT 1
		""").fetchone()
		
		if result:
			long_signal = int(result[0])
			short_signal = int(result[1])
			leverage = int(result[2])
			solid_max_loss = float(result[3])
			step_max_loss = float(result[4])

			logger.info(
				f"Получены: long_signal = {long_signal} ;\n"
				f"Получены: short_signal = {short_signal} ;\n"
				f"Получены: leverage = {leverage} ;\n"
				f"Получены: solid_max_loss = {solid_max_loss} ;\n"
				f"Получены: step_max_loss = {step_max_loss} .\n"
			)

		else:
			logger.warning("temp_trading пуста, используем сигналы по умолчанию")
			long_signal = 1
			short_signal = -1
			leverage = 1
			solid_max_loss = 0.01
			step_max_loss = 0.001
			
	except Exception as e:
		logger.error(f"Ошибка получения сигналов: {e}")
		long_signal = 1
		short_signal = -1
		leverage = 1
		solid_max_loss = 0.01
		step_max_loss = 0.001
	
	return long_signal, short_signal, leverage, solid_max_loss, step_max_loss
