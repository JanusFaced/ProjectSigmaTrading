import polars as pl
import dataFrameDownloader
from strategies import (
	trend_cross_hama,
	trend_roc,
	trend_envelopes, 
	line_hama,
	contr_trend,
	contr_envelopes,
	contr_hamacd,
	corr_regression,
	corr_pirson,
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

	if firstName == "trend_cross_hama":
		trend_cross_hama.main(inputMessage)
	elif firstName == "trend_roc":
		trend_roc.main(inputMessage)
	elif firstName == "trend_envelopes":
		trend_envelopes.main(inputMessage)
	elif firstName == "line_hama":
		line_hama.main(inputMessage)
	elif firstName == "contr_trend":
		contr_trend.main(inputMessage)
	elif firstName == "contr_envelopes":
		contr_envelopes.main(inputMessage)
	elif firstName == "contr_hamacd":
		contr_hamacd.main(inputMessage)
	elif firstName == "corr_regression":
		corr_regression.main(inputMessage)
	elif firstName == "corr_pirson":
		corr_pirson.main(inputMessage)
		
	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()
