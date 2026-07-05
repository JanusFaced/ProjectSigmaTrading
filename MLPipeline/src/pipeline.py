from typing import Any
import dataFrameDownloader
from strategies import moving
from strategies import channel
from strategies import forecast
from strategies import modeling
import trading_simulator
import imitation_connector
import filters
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any]) -> None:
	dataFrame: pd.DataFrame = dataFrameDownloader.main(inputMessage)

	if inputMessage["strategy"] == "moving":
		dataFrame = moving.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "channel":
		dataFrame = channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "forecast":
		dataFrame = forecast.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling":
		dataFrame = modeling.main(inputMessage, dataFrame)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'real':
		pass

if __name__ == "__main__":

	mode = 'stats'
	testMode = 'cumul'
	target_year_profit = 30.0

	listNameExchange = ['binance']
	listSymbol = [
		'ETH',
		'BNB',
		'SOL',
		'TRX',
		'ADA',
	]
	listTypeMarket = ['futures']
	listTimeFrame = [
		'8min',
		'18min',
		'36min',
		'48min',
	]
	listStrategy = [
		'moving',
		'channel',
		'forecast',
		'modeling'
	]

	listMSGs = []
	for nameExchange in listNameExchange:
		for typeMarket in listTypeMarket:
			for timeFrame in listTimeFrame:
				for symbol in listSymbol:
					for strategy in listStrategy:
						listMSGs.append({
							'mode': mode,
							'testMode': testMode,
							'nameExchange': nameExchange,
							'symbol': symbol,
							'type': typeMarket,
							'timeFrame': timeFrame,
							'strategy': strategy
						})

	lenthCombi = len(listMSGs)
	logger.info(f"full lenth combination = {lenthCombi}")

	if mode in ["stats", "imitation"]:
		listMSGs = filters.forImitation(listMSGs=listMSGs, target_year_profit=target_year_profit)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for imitation lenth combination = {lenthCombi}")
	elif mode == "real":
		listMSGs = filters.forReal(listMSGs=listMSGs, target_year_profit=target_year_profit)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for real lenth combination = {lenthCombi}")

	if mode != 'stats':
		for msg in listMSGs:
			try:
				main(msg)
			except Exception as e:
				logger.info(f"error: {e}")

	if mode in ['stats', 'test']:
		filters.makeStats(listSymbol=listSymbol, listTimeFrame=listTimeFrame, listStrategy=listStrategy)