from typing import Any
import dataFrameDownloader
from strategies import (
	fixvol, floatvol,
	opt_moving, opt_trend, opt_stochastic, opt_cross_ma, opt_fixvol_moving, opt_floatvol_moving,
	modeling, correlation
)
import trading_simulator
import imitation_connector
from filters_kit import filter_new, filter_exist
import makeStats
from duckDB_setup import close_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any]) -> None:
	nameStrategy = inputMessage["strategy"]
	splitNameStrategy = nameStrategy.split(":")
	firstName = splitNameStrategy[0]
	lastName = splitNameStrategy[1]

	if lastName == 'I':
		inputMessage['strategy'] = firstName

	elif lastName == 'II':
		inputMessage['strategy'] = ":".join([
			firstName,
			inputMessage['factor'],
			inputMessage['typeFactor'],
			inputMessage['factorExchange']
		])
	
	dataFrameDownloader.main(
		nameExchange=inputMessage['nameExchange'],
		symbol=inputMessage['symbol'],
		type=inputMessage['type'],
		timeFrame=inputMessage['timeFrame'],
		mode=inputMessage['mode'],
		factor=inputMessage['factor'],
		typeFactor=inputMessage['typeFactor'],
		factorExchange=inputMessage['factorExchange']
	)

	if firstName == "fixvol":
		fixvol.main(inputMessage)
	elif firstName == "floatvol":
		floatvol.main(inputMessage)
	elif firstName == "opt_moving":
		opt_moving.main(inputMessage)
	elif firstName == "opt_cross_ma":
		opt_cross_ma.main(inputMessage)
	elif firstName == "opt_trend":
		opt_trend.main(inputMessage)
	elif firstName == "opt_stochastic":
		opt_stochastic.main(inputMessage)
	elif firstName == "opt_fixvol_moving":
		opt_fixvol_moving.main(inputMessage)
	elif firstName == "opt_floatvol_moving":
		opt_floatvol_moving.main(inputMessage)
	elif firstName == "modeling":
		modeling.main(inputMessage)
	elif firstName == "correlation":
		correlation.main(inputMessage)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()