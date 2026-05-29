from typing import Any
import dataFrameDownloader
import plClassification
import plRegression
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any]) -> None:

	dataFrame: pd.DataFrame = dataFrameDownloader.main(
		symbol=inputMessage['symbol'],
		nameExchange='binance',
		timeFrame=inputMessage['timeFrame']
	)

	if inputMessage['task'] == "classification":
		plClassification.main(inputMessage, dataFrame)

	elif inputMessage['task'] == "regression":
		plRegression.main(inputMessage, dataFrame)

if __name__ == "__main__":

	listMSGs = [
#		{'symbol': 'BTC', 'timeFrame': '15min', "task": "classification"},
#		{'symbol': 'ETH', 'timeFrame': '15min', "task": "classification"},
#		{'symbol': 'BNB', 'timeFrame': '15min', "task": "classification"},
#
#		{'symbol': 'BTC', 'timeFrame': '30min', "task": "classification"},
#		{'symbol': 'ETH', 'timeFrame': '30min', "task": "classification"},
#		{'symbol': 'BNB', 'timeFrame': '30min', "task": "classification"},
#
#		{'symbol': 'BTC', 'timeFrame': '1h', "task": "classification"},
#		{'symbol': 'ETH', 'timeFrame': '1h', "task": "classification"},
#		{'symbol': 'BNB', 'timeFrame': '1h', "task": "classification"},



		{'symbol': 'BTC', 'timeFrame': '15min', "task": "regression"},
		{'symbol': 'ETH', 'timeFrame': '15min', "task": "regression"},
		{'symbol': 'BNB', 'timeFrame': '15min', "task": "regression"},

		{'symbol': 'BTC', 'timeFrame': '30min', "task": "regression"},
		{'symbol': 'ETH', 'timeFrame': '30min', "task": "regression"},
		{'symbol': 'BNB', 'timeFrame': '30min', "task": "regression"},

		{'symbol': 'BTC', 'timeFrame': '1h', "task": "regression"},
		{'symbol': 'ETH', 'timeFrame': '1h', "task": "regression"},
		{'symbol': 'BNB', 'timeFrame': '1h', "task": "regression"},
	]

	for msg in listMSGs:
		main(msg)