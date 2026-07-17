from typing import Any
import dataFrameDownloader
from strategies import moving, channel, forecast, modeling, pattern, correlation
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

	if firstName == "moving":
		moving.main(inputMessage)
	elif firstName == "channel":
		channel.main(inputMessage)
	elif firstName == "forecast":
		forecast.main(inputMessage)
	elif firstName == "modeling":
		modeling.main(inputMessage)
	elif firstName == "pattern":
		pattern.main(inputMessage)
	elif firstName == "correlation":
		correlation.main(inputMessage)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage)
	elif inputMessage['mode'] == 'real':
		pass

	close_duckdb()