import os
import sys
import time
from datetime import datetime
from dataBaseModels import Signal, Backtest, Trade
from dataBaseModels import get_session, close_session
from logger_setup import get_logger

logger = get_logger(__name__)

def saveBacktests(inputData: dict) -> None:
	tryCount, maxTryOnes = 0, 3
	while True:
		dataBaseSession = get_session()
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
			break
		
		except Exception as e:
			dataBaseSession.rollback()
			logger.error(f"Error saving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(1)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def receiveSignals(nameStrategy: str) -> dict:
	tryCount, maxTryOnes = 0, 3
	while True:
		dataBaseSession = get_session()
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
			break

		except Exception as e:
			dataBaseSession.rollback()
			logger.error(f"Error receiving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(1)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

	return receiveList

def sendSignals(nameStrategy: str, signalPuck: dict) -> None:
	tryCount, maxTryOnes = 0, 3
	while True:
		dataBaseSession = get_session()
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
			break

		except Exception as e:
			dataBaseSession.rollback()
			logger.error(f"Error saving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(1)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def sendTrads(nameStrategy: str, signalPuck: dict) -> int:
	tryCount, maxTryOnes = 0, 3
	while True:
		dataBaseSession = get_session()

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
			break

		except Exception as e:
			dataBaseSession.rollback()
			logger.error(f"Error saving trads! Try again! {tryCount}")
			tryCount += 1
			time.sleep(1)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')