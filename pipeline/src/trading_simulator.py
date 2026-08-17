from typing import Any, TypedDict, Dict
import matplotlib.pyplot as plt
import polars as pl
import numpy as np
import sys
import os
import saveToDB
import fastBackTester
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
	testMode = inputMessage['testMode']

	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']

	db = get_duckdb()

	dataFrame = db.execute("""
		SELECT * FROM temp_trading 
		ORDER BY datetime
	""").pl()

	shift_signal: int = 2
	
	dataFrame = dataFrame.with_columns([
		pl.col("long_signal").shift(shift_signal).alias("long_signal"),
		pl.col("short_signal").shift(shift_signal).alias("short_signal"),
	])

	send_list = fastBackTester.coreBacktester(dataFrame, testMode)

	'''
	cash_balance_body = send_list['balanceBody']
	cash_balance_cold = send_list['balanceCold']

	dataFrame = dataFrame.with_columns([
		pl.Series('cash_balance_body', cash_balance_body),
		pl.Series('cash_balance_cold', cash_balance_cold),
	])

	dataFrame = dataFrame.with_columns([
		(pl.col('cash_balance_body') + pl.col('cash_balance_cold')).alias('deposite')
	])

	tempDF = dataFrame.select(['signalUpBoard', 'signalDownBoard'])
	superName = str(output_dir) + f'/boards_{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}.png'
	plt.plot(tempDF['signalUpBoard'], color='green')
	plt.plot(tempDF['signalDownBoard'], color='red')
	plt.savefig(superName)
	plt.close()
	'''

	return send_list

def backTestAnalyst(
		inputMessage: dict[str, Any],
		report: Dict,
		analystMode: bool = False
	) -> dict:

	testMode = inputMessage['testMode']
	nameExchange = inputMessage['nameExchange']
	symbol = inputMessage['symbol']
	type = inputMessage['type']
	timeFrame = inputMessage['timeFrame']
	strategy = inputMessage['strategy']
	nameStrategy = f"{strategy}_{symbol}_{timeFrame}_{type}_{nameExchange}"

	balanceBody = report['balanceBody']
	balanceCold = report['balanceCold']
	
	winrate = [report['general']['winrate'], report['long']['winrate'], report['short']['winrate']]
	freqTrads = [report['general']['freqTrads'], report['long']['freqTrads'], report['short']['freqTrads']]
	averageLengthTrade = [report['general']['averageLengthTrade'], report['long']['averageLengthTrade'], report['short']['averageLengthTrade']]
	averageProfitSize = [report['general']['averageProfitSize'], report['long']['averageProfitSize'], report['short']['averageProfitSize']]
	maxProfitSize = [report['general']['maxProfitSize'], report['long']['maxProfitSize'], report['short']['maxProfitSize']]
	averageLossSize = [report['general']['averageLossSize'], report['long']['averageLossSize'], report['short']['averageLossSize']]
	maxLossSize = [report['general']['maxLossSize'], report['long']['maxLossSize'], report['short']['maxLossSize']]
	trads = [report['general']['trads'], report['long']['trads'], report['short']['trads']]
	maxLengthTrade = [report['general']['maxLengthTrade'], report['long']['maxLengthTrade'], report['short']['maxLengthTrade']]
	minLenthTrade = [report['general']['minLenthTrade'], report['long']['minLenthTrade'], report['short']['minLenthTrade']]
	amountStopLoss = [report['general']['amountStopLoss'], report['long']['amountStopLoss'], report['short']['amountStopLoss']]
	amountTakeProfit = [report['general']['amountTakeProfit'], report['long']['amountTakeProfit'], report['short']['amountTakeProfit']]
	amountLossSignal = [report['general']['amountLossSignal'], report['long']['amountLossSignal'], report['short']['amountLossSignal']]
	amountProfitSignal = [report['general']['amountProfitSignal'], report['long']['amountProfitSignal'], report['short']['amountProfitSignal']]

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

	if analystMode == False:
		logger.info(f'========== ANALYST for {nameStrategy} ==========')
		logger.info(f'winrate {winrate[0]} (L:{winrate[1]}|S:{winrate[2]}) %')
		logger.info(f'freqTrads {freqTrads[0]} (L:{freqTrads[1]}|S:{freqTrads[2]}) trads/candle')
		logger.info(f'trads {trads[0]} (L:{trads[1]}|S:{trads[2]})')
		logger.info(f"stopLoss {amountStopLoss[0]} (L:{amountStopLoss[1]}|S:{amountStopLoss[2]})")
		logger.info(f"takeProfit {amountTakeProfit[0]} (L:{amountTakeProfit[1]}|S:{amountTakeProfit[2]})")
		logger.info(f"lossSignal {amountLossSignal[0]} (L:{amountLossSignal[1]}|S:{amountLossSignal[2]})")
		logger.info(f"profitSignal {amountProfitSignal[0]} (L:{amountProfitSignal[1]}|S:{amountProfitSignal[2]})")
		logger.info(f'maxProfitSize {maxProfitSize[0]} (L:{maxProfitSize[1]}|S:{maxProfitSize[2]}) %')
		logger.info(f'averageProfitSize {averageProfitSize[0]} (L:{averageProfitSize[1]}|S:{averageProfitSize[2]}) %')
		logger.info(f'averageLossSize {averageLossSize[0]} (L:{averageLossSize[1]}|S:{averageLossSize[2]}) %')
		logger.info(f'maxLossSize {maxLossSize[0]} (L:{maxLossSize[1]}|S:{maxLossSize[2]}) %')
		logger.info(f'max_time_reborn {max_time_reborn} candles')
		logger.info(f'maxLengthTrade {maxLengthTrade[0]} (L:{maxLengthTrade[1]}|S:{maxLengthTrade[2]}) candles')
		logger.info(f'minLenthTrade {minLenthTrade[0]} (L:{minLenthTrade[1]}|S:{minLenthTrade[2]}) candles')
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

		listReport = {
			"strategy": nameStrategy,
			"year_profit": geom_mean_profit,
			"max_drawdown": max_drawdawn,
			"sharp": sharp_classic
		}
		saveToDB.saveBacktests(inputData=listReport)
		logger.info('saveBacktests!')

	else:

		optimization_index = (
			geom_mean_profit
		)

		listReport = {
			"strategy": nameStrategy,
			"year_profit": geom_mean_profit,
			"max_drawdown": max_drawdawn,
			"sharp": sharp_classic,
			"optiMetric": optimization_index
		}

	return listReport




