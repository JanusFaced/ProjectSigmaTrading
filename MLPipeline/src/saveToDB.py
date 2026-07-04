import os
import sys
from datetime import datetime
from dataBaseModels import Session, Signal, Backtest, Trade
from logger_setup import get_logger

logger = get_logger(__name__)

def saveBacktests(inputData: dict) -> None:
	dataBaseSession = Session()

	try:
		exist = dataBaseSession.query(Backtest).filter(
			Backtest.strategy == inputData['strategy']
		).first()
		
		if exist:
			exist.year_profit = inputData['year_profit']
			exist.max_drawdown = inputData['max_drawdown']
			exist.sharp = inputData['sharp']
			exist.datetime = datetime.now()
			logger.info(f"Updated {inputData['strategy']} -> Y:{inputData['year_profit']} (id={exist.id})")

		else:
			newBacktest = Backtest(
				strategy=inputData['strategy'],
				year_profit=inputData['year_profit'],
				max_drawdown=inputData['max_drawdown'],
				sharp=inputData['sharp']
			)
			dataBaseSession.add(newBacktest)
			logger.info(f"Created {inputData['strategy']} -> Y:{inputData['year_profit']} (id={newBacktest.id})")
		
		dataBaseSession.commit()

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
		raise
	
	finally:
		dataBaseSession.close()

def receiveSignals(nameStrategy: str) -> dict:
	dataBaseSession = Session()

	try:
		exist = dataBaseSession.query(Signal).filter(
			Signal.strategy == nameStrategy
		).first()
		
		if exist:
			receiveList = {
				'exist': True,
				'status': exist.status,
				'fiat': exist.fiat,
				'active': exist.active,
				'datetime': exist.datetime
			}
			logger.info(f"{nameStrategy} is exist!")

		else:
			receiveList = {'exist': False}
			logger.info(f"{nameStrategy} is NOT exist!")

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error receiving signal: {e}")
		raise
	
	finally:
		dataBaseSession.close()

	return receiveList

def sendSignals(nameStrategy: str, signalPuck: dict) -> int:
	dataBaseSession = Session()

	try:
		exist = dataBaseSession.query(Signal).filter(
			Signal.strategy == nameStrategy
		).first()
		
		if exist:
			exist.long_signal = signalPuck['long_signal']
			exist.short_signal = signalPuck['short_signal']
			exist.mode = signalPuck['mode']
			exist.status = signalPuck['status']
			exist.fiat = signalPuck['fiat']
			exist.active = signalPuck['active']
			exist.deposit = signalPuck['deposit']
			exist.datetime = datetime.now()
			logger.info(f"Updated {nameStrategy} -> L:{signalPuck['long_signal']} | S:{signalPuck['short_signal']} (id={exist.id})")

		else:
			newSignal = Signal(
				strategy=nameStrategy,
				long_signal=signalPuck['long_signal'],
				short_signal=signalPuck['short_signal'],
				mode=signalPuck['mode'],
				status=signalPuck['status'],
				fiat=signalPuck['fiat'],
				active=signalPuck['active'],
				deposit=signalPuck['deposit']
			)
			dataBaseSession.add(newSignal)
			logger.info(f"Created {nameStrategy} -> L:{signalPuck['long_signal']} | S:{signalPuck['short_signal']} with id={newSignal.id}")
		
		dataBaseSession.commit()
		resultWork = True

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
		resultWork = False
	
	finally:
		dataBaseSession.close()

	return resultWork

def receiveTrads(nameStrategy: str) -> bool:
	dataBaseSession = Session()

	try:
		signal = dataBaseSession.query(Signal).filter(
			Signal.strategy == nameStrategy
		).first()
		trades_count = dataBaseSession.query(Trade).filter(
			Trade.signal_id == signal.id
		).count()

		if trades_count > 0:
			resultWork = False
			logger.info(f"{nameStrategy} trades is exist!")

		else:
			resultWork = True
			logger.info(f"{nameStrategy} trades is NOT exist!")

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error receiving signal: {e}")
		raise
	
	finally:
		dataBaseSession.close()

	return resultWork

def sendTrads(nameStrategy: str, signalPuck: dict) -> int:
	dataBaseSession = Session()

	try:
		signal = dataBaseSession.query(Signal).filter(
			Signal.strategy == nameStrategy
		).first()

		new_trade = Trade(
			signal_id=signal.id,
			long_signal=signalPuck['long_signal'],
			short_signal=signalPuck['short_signal'],
			fiat=signalPuck['fiat'],
			active=signalPuck['active'],
			deposit=signalPuck['deposit'],
			datetime=datetime.now()
		)
		
		dataBaseSession.add(new_trade)
		dataBaseSession.commit()
		resultWork = True

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
		resultWork = False
	
	finally:
		dataBaseSession.close()

	return resultWork