import polars as pl
import numpy as np
import numpy.typing as npt
import os
import sys
import time
from datetime import datetime
from sqlalchemy import text
from dataBaseModels import (
	DATABASE_URL,
	Signal,
	Backtest,
	Trade,
	TradeADJ,
	CurrentPortfolio,
	HistoryPortfolio,
	get_session,
	close_session,
)
from logger_setup import get_logger

logger = get_logger(__name__)

def saveEquity(
		tableName: str,
		equityDataframe: pl.DataFrame,
	) -> None:

	tryCount, maxTryOnes = 0, 7
	while True:
		try:
			equityDataframe.write_database(
				table_name=tableName,
				connection=DATABASE_URL,
				engine="adbc",
				if_table_exists="replace",
			)

			logger.info(f' --> Table: {tableName} is saved! <--')
			break
	
		except Exception as e:
			logger.error(f"Error saving table! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e

def saveBacktests(inputData: dict) -> None:
	tryCount, maxTryOnes = 0, 7
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
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error saving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def receiveSignals(nameStrategy: str) -> dict:
	tryCount, maxTryOnes = 0, 7
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
					'stop_loss': exist.stop_loss,
					'weight_portfolio': exist.weight_portfolio,
					'current_position': exist.current_position,
					'datetime': exist.datetime
				}
				logger.info(f"{nameStrategy} is exist!")
			else:
				receiveList = {'exist': False}
				logger.info(f"{nameStrategy} is NOT exist!")
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error receiving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

	return receiveList

def sendSignals(nameStrategy: str, signalPuck: dict) -> None:
	tryCount, maxTryOnes = 0, 7
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
				exist.stop_loss = signalPuck['stop_loss']
				exist.adj_deposite = signalPuck['adj_deposite']
				exist.current_position = signalPuck['current_position']
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
					deposit=signalPuck['deposit'],
					stop_loss=signalPuck['stop_loss'],
					weight_portfolio=signalPuck['weight_portfolio'],
					adj_deposite=signalPuck['adj_deposite'],
					current_position=signalPuck['current_position']
				)
				dataBaseSession.add(newSignal)
				logger.info(f"Created {nameStrategy} -> L:{signalPuck['long_signal']} | S:{signalPuck['short_signal']} with id={newSignal.id}")
			
			dataBaseSession.commit()
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error saving signal! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def sendTrads(nameStrategy: str, signalPuck: dict) -> int:
	tryCount, maxTryOnes = 0, 7
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
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error saving trads! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def sendAdjTrads(nameStrategy: str, signalPuck: dict) -> int:
	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()

		try:
			signal = dataBaseSession.query(Signal).filter(
				Signal.strategy == nameStrategy
			).first()

			new_trade = TradeADJ(
				signal_id=signal.id,
				adj_deposite=signalPuck['adj_deposite'],
				datetime=datetime.now()
			)
			
			dataBaseSession.add(new_trade)
			dataBaseSession.commit()
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error saving trads! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def receive_portfolio(name_portfolio: str) -> dict:
	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()
		try:
			exist = dataBaseSession.query(CurrentPortfolio).filter(
				CurrentPortfolio.name_portfolio == name_portfolio
			).first()
			if exist:
				receiveList = {
					'exist': True,
					'portfolio': exist.portfolio,
					'full_profit': exist.full_profit,
					'year_profit': exist.year_profit,
					'max_drawdown': exist.max_drawdown,
					'sharp': exist.sharp,
					'profit_factor': exist.profit_factor,
					'datetime': exist.datetime,
				}
				logger.info(f"{name_portfolio} is exist!")
			else:
				receiveList = {'exist': False}
				logger.info(f"{name_portfolio} is NOT exist!")
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error receive_portfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

	return receiveList

def send_portfolio(name_portfolio: str, signalPuck: dict) -> None:
	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()
		try:
			exist = dataBaseSession.query(CurrentPortfolio).filter(
				CurrentPortfolio.name_portfolio == name_portfolio
			).first()
			
			if exist:
				exist.portfolio = signalPuck['portfolio']
				exist.full_profit = signalPuck['full_profit']
				exist.year_profit = signalPuck['year_profit']
				exist.max_drawdown = signalPuck['max_drawdown']
				exist.sharp = signalPuck['sharp']
				exist.profit_factor = signalPuck['profit_factor']
				exist.datetime = signalPuck['dataBaseDateTime']

				logger.info(f"Save {name_portfolio}")

			else:
				newData = CurrentPortfolio(
					name_portfolio=name_portfolio,
					portfolio=signalPuck['portfolio'],
					full_profit=signalPuck['full_profit'],
					year_profit=signalPuck['year_profit'],
					max_drawdown=signalPuck['max_drawdown'],
					sharp=signalPuck['sharp'],
					profit_factor=signalPuck['profit_factor'],
				)
				dataBaseSession.add(newData)
				
				logger.info(f"Created {name_portfolio}")
			
			dataBaseSession.commit()
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.error(f"Error saving CurrentPortfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

def send_history_portfolio(name_portfolio: str, signalPuck: dict) -> int:
	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()

		try:
			current_portfolio = dataBaseSession.query(CurrentPortfolio).filter(
				CurrentPortfolio.name_portfolio == name_portfolio
			).first()

			new_data = HistoryPortfolio(
				current_portfolio_id=current_portfolio.id,
				portfolio=signalPuck['portfolio'],
				datetime=datetime.now()
			)
			
			dataBaseSession.add(new_data)
			dataBaseSession.commit()

			logger.info(f'HistoryPortfolio is saved!')

			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.info(f"{e}")
			logger.error(f"Error saving HistoryPortfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')


def parser_portfolio(listOfStrats: list) -> float:
	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()
		try:
			rows = dataBaseSession.query(Signal.deposit).filter(Signal.strategy.in_(listOfStrats)).all()
			logger.info(f" + Rows of strats' deposits is get!")
			
			if rows != None:
				deposits = np.array([r[0] for r in rows], dtype=float)
				portfolio = float(np.sum(deposits))
				logger.info(f"rows is exist!")
			
			else:
				portfolio = -100
				logger.info(f"rows is NOT exist!")
			
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.info(f"{e}")
			logger.error(f"Error parser_portfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

	return portfolio


def rebalance_portfolio(
		portfolio: float,
		asset_weights: dict
	) -> None:

	DEFAULT_LONG_SIGNAL = 1
	DEFAULT_SHORT_SIGNAL = -1
	DEFAULT_MODE = "imitation"
	DEFAULT_STATUS = "work"
	DEFAULT_STOP_LOSS = 0.01

	tryCount, maxTryOnes = 0, 7

	while True:
		dataBaseSession = get_session()
		try:
			for strategy_name, weight in asset_weights.items():
				fiat = portfolio * weight
				deposit = fiat
				adj_deposite = deposit / weight

				exist = (
					dataBaseSession.query(Signal)
					.filter(Signal.strategy == strategy_name)
					.first()
				)

				if exist:
					exist.long_signal = DEFAULT_LONG_SIGNAL
					exist.short_signal = DEFAULT_SHORT_SIGNAL
					exist.mode = DEFAULT_MODE
					exist.status = DEFAULT_STATUS
					exist.weight_portfolio = weight
					exist.fiat = fiat
					exist.active = 0.0
					exist.deposit = deposit
					exist.stop_loss = DEFAULT_STOP_LOSS
					exist.adj_deposite = adj_deposite
					exist.current_position = fiat
					exist.datetime = datetime.now()

					logger.info(
						f"Rebalanced {strategy_name}: weight={weight}, "
						f"fiat={fiat}, deposit={deposit}, "
						f"adj_deposite={adj_deposite} (id={exist.id})"
					)

				else:
					newSignal = Signal(
						strategy=strategy_name,
						long_signal=DEFAULT_LONG_SIGNAL,
						short_signal=DEFAULT_SHORT_SIGNAL,
						mode=DEFAULT_MODE,
						status=DEFAULT_STATUS,
						weight_portfolio=weight,
						fiat=fiat,
						active=0.0,
						deposit=deposit,
						stop_loss=DEFAULT_STOP_LOSS,
						adj_deposite=adj_deposite,
						current_position=fiat,
						datetime=datetime.now(),
					)
					dataBaseSession.add(newSignal)

					logger.info(
						f"Created {strategy_name}: weight={weight}, "
						f"fiat={fiat}, deposit={deposit}, "
						f"adj_deposite={adj_deposite}"
					)

			dataBaseSession.commit()
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except Exception:
				logger.info("rollback is fail!")
			logger.error(f"Error rebalancing portfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e

		finally:
			close_session()
			logger.info("Сессия с базой данных закрыта!")


def get_chart_portfolio(name_portfolio: str) -> int:

	tryCount, maxTryOnes = 0, 7
	while True:
		dataBaseSession = get_session()

		try:
			current_portfolio = (
				dataBaseSession.query(CurrentPortfolio)
				.filter(CurrentPortfolio.name_portfolio == name_portfolio)
				.first()
			)

			if current_portfolio is None:
				logger.warning(f"Portfolio {name_portfolio} not found")
				chart = np.array([], dtype=float)

			rows = (
				dataBaseSession.query(HistoryPortfolio.portfolio)
				.filter(HistoryPortfolio.current_portfolio_id == current_portfolio.id)
				.order_by(HistoryPortfolio.datetime.asc())
				.all()
			)
			
			if not rows:
				logger.info(f"No history for portfolio {name_portfolio}")
				chart = np.array([], dtype=float)

			else:
				chart = np.array([r[0] for r in rows], dtype=float)

			logger.info(
				f"Chart for {name_portfolio}: {chart.size} points, "
			)
			break

		except Exception as e:
			try:
				dataBaseSession.rollback()
			except:
				logger.info('rollback is fail!')
			logger.info(f"{e}")
			logger.error(f"Error get_chart_portfolio! Try again! {tryCount}")
			tryCount += 1
			time.sleep(tryCount)
			if tryCount > maxTryOnes:
				raise e
		
		finally:
			close_session()
			logger.info('Сессия с базой данных закрыта!')

	return chart

