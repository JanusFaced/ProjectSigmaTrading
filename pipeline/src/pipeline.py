import polars as pl
import dataFrameDownloader
from strategies import (
	opt_moving, opt_cross_ma, opt_trend,
	opt_stochastic, opt_bollinger, opt_keltner,
	opt_envelopes, opt_modeling, opt_correlation,
	opt_lrcurve, opt_lrchannel, opt_kama,

	hurst_moving, hurst_cross_ma, hurst_trend,
	hurst_stochastic, hurst_bollinger, hurst_keltner,
	hurst_envelopes, hurst_modeling, hurst_correlation,
	hurst_lrcurve, hurst_lrchannel,
)
import trading_simulator
import imitation_connector
from duckDB_setup import close_duckdb
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict) -> None:
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
	elif firstName == "opt_kama":
		opt_kama.main(inputMessage)
		
	elif firstName == "hurst_moving":
		hurst_moving.main(inputMessage)
	elif firstName == "hurst_cross_ma":
		hurst_cross_ma.main(inputMessage)
	elif firstName == "hurst_trend":
		hurst_trend.main(inputMessage)
	elif firstName == "hurst_stochastic":
		hurst_stochastic.main(inputMessage)
	elif firstName == "hurst_bollinger":
		hurst_bollinger.main(inputMessage)
	elif firstName == "hurst_keltner":
		hurst_keltner.main(inputMessage)
	elif firstName == "hurst_envelopes":
		hurst_envelopes.main(inputMessage)
	elif firstName == "hurst_modeling":
		hurst_modeling.main(inputMessage)
	elif firstName == "hurst_correlation":
		hurst_correlation.main(inputMessage)
	elif firstName == "hurst_lrcurve":
		hurst_lrcurve.main(inputMessage)
	elif firstName == "hurst_lrchannel":
		hurst_lrchannel.main(inputMessage)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()
