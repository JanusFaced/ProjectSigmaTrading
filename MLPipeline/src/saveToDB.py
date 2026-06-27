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

def sendSignals(inputData: dict) -> None:
	dataBaseSession = Session()

	try:
		exist = dataBaseSession.query(Signal).filter(
			Signal.strategy == inputData['strategy']
		).first()
		
		if exist:
			exist.long_signal = inputData['long_signal']
			exist.short_signal = inputData['short_signal']
			exist.mode = inputData['mode']
			exist.status = inputData['status']
			exist.fiat = inputData['fiat']
			exist.active = inputData['active']
			exist.deposit = inputData['deposit']
			exist.datetime = datetime.now()
			logger.info(f"Updated {inputData['strategy']} -> L:{inputData['long_signal']} | S:{inputData['short_signal']} (id={exist.id})")

		else:
			newSignal = Signal(
				strategy=inputData['strategy'],
				long_signal=inputData['long_signal'],
				short_signal=inputData['short_signal'],
				mode=inputData['mode'],
				status=inputData['status'],
				fiat=inputData['fiat'],
				active=inputData['active'],
				deposit=inputData['deposit']
			)
			dataBaseSession.add(newSignal)
			logger.info(f"Created {inputData['strategy']} -> L:{inputData['long_signal']} | S:{inputData['short_signal']} with id={newSignal.id}")
		
		dataBaseSession.commit()

	except Exception as e:
		dataBaseSession.rollback()
		logger.error(f"Error saving signal: {e}")
		raise
	
	finally:
		dataBaseSession.close()