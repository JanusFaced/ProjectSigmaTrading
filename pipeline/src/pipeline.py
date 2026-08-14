from typing import Any
import dataFrameDownloader
from strategies import (
	opt_moving, opt_trend, opt_stochastic,
	opt_cross_ma, opt_bollinger, opt_keltner,
	opt_envelopes, opt_modeling, opt_correlation,
	opt_lrcurve, opt_lrchannel,
	ada_moving, ada_trend, ada_modeling, ada_correlation, ada_lrcurve, ada_lrchannel
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

	if firstName == "opt_moving":
		opt_moving.main(inputMessage)
	elif firstName == "opt_cross_ma":
		opt_cross_ma.main(inputMessage)
	elif firstName == "opt_trend":
		opt_trend.main(inputMessage)
	elif firstName == "opt_stochastic":
		opt_stochastic.main(inputMessage)
	elif firstName == "opt_bollinger":
		opt_bollinger.main(inputMessage)
	elif firstName == "opt_keltner":
		opt_keltner.main(inputMessage)
	elif firstName == "opt_envelopes":
		opt_envelopes.main(inputMessage)
	elif firstName == "opt_modeling":
		opt_modeling.main(inputMessage)
	elif firstName == "opt_correlation":
		opt_correlation.main(inputMessage)
	elif firstName == "opt_lrcurve":
		opt_lrcurve.main(inputMessage)
	elif firstName == "opt_lrchannel":
		opt_lrchannel.main(inputMessage)

	elif firstName == "ada_moving":
		ada_moving.main(inputMessage)
	elif firstName == "ada_trend":
		ada_trend.main(inputMessage)
	elif firstName == "ada_modeling":
		ada_modeling.main(inputMessage)
	elif firstName == "ada_correlation":
		ada_correlation.main(inputMessage)
	elif firstName == "ada_lrcurve":
		ada_lrcurve.main(inputMessage)
	elif firstName == "ada_lrchannel":
		ada_lrchannel.main(inputMessage)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()