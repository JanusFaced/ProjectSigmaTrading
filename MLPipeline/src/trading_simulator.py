from typing import Any, TypedDict, Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
import backtrader as bt
import saveToDB
from convertorTF import convertorTimeFrame
from duckDB_setup import get_duckdb
from logger_setup import get_logger
from pathlib import Path

logger = get_logger(__name__)
output_dir = Path(__file__).parent / "output"

def main(inputMessage: dict[str, Any]) -> None:
	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	nameStrategy = f"{nameExchange}_{symbol}_{type}_{timeFrame}_{strategy}"
	
	logger.info(f' > Start backtesting {nameStrategy}')
	report = backTester(inputMessage)
	logger.info(' > End backtesting')
	backTestAnalyst(
		inputMessage=inputMessage,
		report=report
	)

def backTester(inputMessage: dict[str, Any]) -> Dict:

	class MyPandasData(bt.feeds.PandasData):
		lines = ('long_signal', 'short_signal')
		params = (('long_signal', 'long_signal'), ('short_signal', 'short_signal'))

	class MyStrategy(bt.Strategy):
		def __init__(self):
			self.long_signal = self.datas[0].lines.long_signal
			self.short_signal = self.datas[0].lines.short_signal
			self.past_deel_long = 0
			self.past_deel_short = 0
			self.my_pose = 'none'
			self.cash_balance_body = []
			self.cash_balance_cold = []

		def next(self):
			if (self.long_signal[0] == -1) and (self.my_pose == 'none'):
				self.buy()
				self.my_pose = 'long'
			
			elif (self.long_signal[0] == 1) and (self.my_pose == 'long'):
				self.close()
				self.my_pose = 'none'
			
			if (self.short_signal[0] == -1) and (self.my_pose == 'short'):
				self.close()
				self.my_pose = 'none'
				
			elif (self.short_signal[0] == 1) and (self.my_pose == 'none'):
				self.sell()
				self.my_pose = 'short'

			full_depo = self.broker.getvalue()

			if full_depo < max_lot:
				self.cash_balance_body.append(full_depo)
				self.cash_balance_cold.append(0)

			else:
				cold_depo = full_depo - max_lot
				self.cash_balance_body.append(max_lot)
				self.cash_balance_cold.append(cold_depo)


	class CustomCashSizer(bt.Sizer):
		def _getsizing(self, comminfo, cash, data, isbuy):
			if isbuy:
				price = data.close[0]
				if cash >= min_lot:

					if cash < max_lot:
						size = cash/price
						return size

					else:
						size = max_lot/price
						return size

				else:
					return 0

			else:
				price = data.close[0]
				if cash >= min_lot:

					if cash < max_lot:
						size = cash/price
						return size

					else:
						size = max_lot/price
						return size

				else:
					return 0

	class FractionalCommission(bt.CommInfoBase):
		params = (
			('stocklike', True),
			('commtype', bt.CommInfoBase.COMM_PERC),
		)

		def getsize(self, price, cash):
			return cash/price

	db = get_duckdb()
	dataFrame = db.execute("""
		SELECT datetime, open, high, low, close, volume, long_signal, short_signal 
		FROM temp_trading 
		ORDER BY datetime
	""").df()

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	start_fiat = 100
	shift_signal = 2
	leverage = 1
	spred = 0.001
	fees = 0.001 + spred
	min_lot = 10
	max_lot = start_fiat

	dataFrame = dataFrame.copy()
	dataFrame.set_index('datetime', inplace=True)
	dataFrame['long_signal'] = dataFrame['long_signal'].shift(shift_signal)
	dataFrame['short_signal'] = dataFrame['short_signal'].shift(shift_signal)

	data = MyPandasData(dataname=dataFrame)
	cerebro = bt.Cerebro()
	cerebro.adddata(data)
	cerebro.addstrategy(MyStrategy)
	cerebro.addsizer(CustomCashSizer)
	cerebro.broker.set_cash(start_fiat)
	cerebro.broker.setcommission(
		commission=fees,
		leverage=leverage
	)
	cerebro.broker.addcommissioninfo(FractionalCommission())

	cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analysis")

	backtest_result = cerebro.run()[0]

	analyzer = backtest_result.analyzers.trade_analysis.get_analysis()
	cash_balance_body = backtest_result.cash_balance_body
	cash_balance_cold = backtest_result.cash_balance_cold
	trads = analyzer.total.total

	freq_trads = trads/len(dataFrame)
	amount_stop_loss = 0
	amount_take_profit = 0

	try:
		amount_profit_signal = analyzer.won.total
	except:
		amount_profit_signal = 0

	try:
		amount_loss_signal = analyzer.lost.total
	except:
		amount_loss_signal = 0

	if (trads > 0) and (amount_profit_signal > 0) and (amount_loss_signal > 0):
		average_profit_size = analyzer.won.pnl.average/start_fiat
		average_loss_size = analyzer.lost.pnl.average/start_fiat
		max_profit_size = analyzer.won.pnl.max/start_fiat
		max_loss_size = analyzer.lost.pnl.max/start_fiat

		average_len_trad = analyzer.len.average
		max_len_trad = analyzer.len.max
		min_len_trad = analyzer.len.min
		win_loss = amount_profit_signal/trads

		win_loss = int(round(100*win_loss, 0))
		freq_trads = int(freq_trads)
		average_len_trad = round(np.mean(average_len_trad),2)

		if (amount_take_profit + amount_profit_signal > 0):
			average_profit_size = round(100*average_profit_size, 2)
			max_profit_size = round(100*max_profit_size, 2)

		else:
			average_profit_size = np.nan
			max_profit_size = np.nan

		if (amount_stop_loss + amount_loss_signal > 0):
			average_loss_size = round(100*average_loss_size, 2)
			max_loss_size = round(100*max_loss_size, 2)

		else:
			average_loss_size = np.nan
			max_loss_size = np.nan

	else:
		win_loss = np.nan
		freq_trads = np.nan
		max_len_trad = np.nan
		average_len_trad = np.nan
		min_len_trad = np.nan
		vector_size_trads = np.nan
		average_profit_size = np.nan
		max_profit_size = np.nan
		average_loss_size = np.nan
		max_loss_size = np.nan	

	send_list = {
		'winrate': win_loss,
		'balanceBody': cash_balance_body,
		'balanceCold': cash_balance_cold,
		'freqTrads': freq_trads,
		'averageLengthTrade': average_len_trad,
		'averageProfitSize': average_profit_size,
		'maxProfitSize': max_profit_size,
		'averageLossSize': average_loss_size,
		'maxLossSize': max_loss_size,
		'trads': trads,
		'maxLengthTrade': max_len_trad,
		'minLenthTrade': min_len_trad,
		'amountStopLoss': amount_stop_loss,
		'amountTakeProfit': amount_take_profit,
		'amountLossSignal': amount_loss_signal,
		'amountProfitSignal': amount_profit_signal,
	}

	#nameResult: str = f"{nameExchange}_{symbol}_{type}_{timeFrame}_{strategy}".lower()
	#fileName: str = f'{output_dir}/backtest_cerebro_{nameResult}.png'
	#cerebro.plot(savefig=True)
	#plt.savefig(fileName)
	#plt.close()

	return send_list

def backTestAnalyst(
		inputMessage: dict[str, Any],
		report: Dict
	) -> None:

	testMode = inputMessage['testMode']

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	winrate = report['winrate']
	balanceBody = report['balanceBody']
	balanceCold = report['balanceCold']
	freqTrads = report['freqTrads']
	averageLengthTrade = report['averageLengthTrade']
	averageProfitSize = report['averageProfitSize']
	maxProfitSize = report['maxProfitSize']
	averageLossSize = report['averageLossSize']
	maxLossSize = report['maxLossSize']
	trads = report['trads']
	maxLengthTrade = report['maxLengthTrade']
	minLenthTrade = report['minLenthTrade']
	amountStopLoss = report['amountStopLoss']
	amountTakeProfit = report['amountTakeProfit']
	amountLossSignal = report['amountLossSignal']
	amountProfitSignal = report['amountProfitSignal']

	integerTimeFrame = convertorTimeFrame(timeFrame)
	multipleTimeFrame = 1440//integerTimeFrame
	yearSize = 365*multipleTimeFrame
	
	period = 500

	start_deposit = 100
	graph_body_old = np.array(balanceBody)
	graph_cold_old = np.array(balanceCold)

	profit_multiple = yearSize/period
	value_part = int(len(graph_body_old)/period)
	solid_len = value_part*period

	graph_body = graph_body_old[-solid_len:]
	graph_cold = graph_cold_old[-solid_len:]

	graph_old = graph_body_old + graph_cold_old
	graph = graph_body + graph_cold

	if (testMode == 'cumul'):
		arr = np.array(graph_body_old)
		drawdowns = (start_deposit - arr)/start_deposit
		max_drawdown = np.max(drawdowns)
		drawdown_indices = np.where(arr >= start_deposit)[0]
		if (len(drawdown_indices) > 1):
			max_time_drawdown = np.max(np.diff(drawdown_indices))
		else:
			max_time_drawdown = 0

	elif (testMode == 'reinvest'):
		arr = np.array(graph_old)
		max_accum = np.maximum.accumulate(arr)
		drawdowns = (max_accum - arr) / max_accum
		max_drawdown = np.max(drawdowns)
		diff = np.diff(max_accum)
		change_indices = np.where(diff != 0)[0]
		change_indices = np.concatenate(([0], change_indices + 1, [len(max_accum)]))
		lengths = np.diff(change_indices)
		max_time_drawdown = np.max(lengths)

	sublists = np.array_split(graph, value_part)
	first_elements = np.array([sublist[0] for sublist in sublists if len(sublist) > 1])
	last_elements = np.array([sublist[-1] for sublist in sublists if len(sublist) > 1])
	rel_diffs_absolute = (last_elements - first_elements)

	sublists = np.array_split(graph_body, value_part)
	first_elements = np.array([sublist[0] for sublist in sublists if len(sublist) > 1])
	rel_diffs_relative = rel_diffs_absolute/first_elements

	sigma = np.std(rel_diffs_relative)
	mean_profit = np.mean(rel_diffs_relative)

	test_part_profit = (graph_old[-1] - graph_old[0])/graph_old[0]
	mean_uno_profit = ( 1 + test_part_profit )**(1/len(graph_old))
	ideal_graph = graph_old[0] * mean_uno_profit ** np.arange(len(graph_old))

	vector_graph_old = np.array(graph_old  )
	vector_ideal_graph = np.array(ideal_graph)

	vector_delta = abs( vector_graph_old - vector_ideal_graph )/vector_graph_old

	mean_delta = np.mean(vector_delta)

	if (sigma > 0):
		sharp = mean_profit/sigma
	
	else:
		sharp = -999

	if (testMode == 'cumul'):
		year_profit = profit_multiple*mean_profit

	elif (testMode == 'reinvest'):
		mean_profit = (1 + (graph[-1] - graph[0])/graph[0])**(1/solid_len)
		year_profit = mean_profit**(period*profit_multiple) - 1

	if ( year_profit == 0 ): year_profit = -1

	if (max_drawdown > 0):
		calmar = year_profit/max_drawdown
	
	else:
		calmar = -999

	if (mean_delta > 0):
		stable_index = 1/mean_delta
	
	else:
		stable_index = -999

	max_time_reborn: int = int(max_time_drawdown)
	geom_mean_profit: float = float(round(100*year_profit, 2))
	max_drawdawn: float = float(round(-100*max_drawdown, 2))
	sharp_classic: float = float(round(sharp, 2))
	stable_index: float = float(round(stable_index, 2))
	calmar: float = float(round(calmar, 2))

	logger.info(f'winrate {winrate} %')
	logger.info(f'trads {trads}')
	logger.info(f'max_time_reborn {max_time_reborn}')
	logger.info(f'geom_mean_profit {geom_mean_profit} %')
	logger.info(f'max_drawdawn {max_drawdawn} %')
	logger.info(f'sharp_classic {sharp_classic}')
	logger.info(f'stable_index {stable_index}')
	logger.info(f'calmar {calmar}')

	nameResult: str = f"{nameExchange}_{symbol}_{type}_{timeFrame}_{strategy}".lower()
	fileName: str = f'{output_dir}/backtest_custom_{nameResult}.png'
	plt.plot(balanceCold)
	plt.plot(balanceBody)
	plt.savefig(fileName)
	plt.close()

	nameStrategy = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"
	inputData = {
		"strategy": nameStrategy,
		"year_profit": geom_mean_profit,
		"max_drawdown": max_drawdawn,
		"sharp": sharp_classic
	}
	saveToDB.saveBacktests(inputData=inputData)
	logger.info('saveBacktests!')