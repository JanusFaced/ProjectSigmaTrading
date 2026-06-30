from typing import Any
import dataFrameDownloader
from strategies import moving
from strategies import trend
from strategies import channel
from strategies import lr_curve
from strategies import lr_channel
from strategies import lr_forecast
from strategies import modeling_curve
from strategies import modeling_channel
from strategies import tree_class
from strategies import forest_class
from strategies import boost_class
import trading_simulator
import imitation_connector
import filters
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any]) -> None:
	dataFrame: pd.DataFrame = dataFrameDownloader.main(inputMessage)

	#__rollingTA__
	if inputMessage["strategy"] == "moving":
		dataFrame = moving.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "trend":
		dataFrame = trend.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "channel":
		dataFrame = channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_curve":
		dataFrame = lr_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_channel":
		dataFrame = lr_channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_forecast":
		dataFrame = lr_forecast.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_curve":
		dataFrame = modeling_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_channel":
		dataFrame = modeling_channel.main(inputMessage, dataFrame)

	#__retrainML__
	elif inputMessage["strategy"] == "tree_class":
		dataFrame = tree_class.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "forest_class":
		dataFrame = forest_class.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "boost_class":
		dataFrame = boost_class.main(inputMessage, dataFrame)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'real':
		pass

if __name__ == "__main__":

	mode = 'stats'

	listNameExchange = ['binance']
	listSymbol = [
		'BTC',
		'ETH',
		'BNB',
		'XRP',
		'SOL',
		'TRX',
		'HYPE',
		'ADA',
		'LINK'
	]
	listTypeMarket = ['futures']
	listTimeFrame = ['1min', '2min', '4min', '8min', '15min', '30min', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
	listStrategy = [
		'moving',
		'trend',
		'channel',
		'lr_curve',
		'lr_channel',
		'lr_forecast',
		'modeling_curve',
		'modeling_channel',
		'tree_class',
		'forest_class',
		'boost_class'
	]

	listMSGs = []
	for nameExchange in listNameExchange:
		for symbol in listSymbol:
			for typeMarket in listTypeMarket:
				for timeFrame in listTimeFrame:
					for strategy in listStrategy:
						listMSGs.append({
							'mode': mode,
							'nameExchange': nameExchange,
							'symbol': symbol,
							'type': typeMarket,
							'timeFrame': timeFrame,
							'strategy': strategy
						})

	lenthCombi = len(listMSGs)
	logger.info(f"full lenth combination = {lenthCombi}")

	if mode == "imitation":
		listMSGs = filters.forImitation(listMSGs=listMSGs, target_year_profit=0.0)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for imitation lenth combination = {lenthCombi}")
	elif mode == "real":
		listMSGs = filters.forReal(listMSGs=listMSGs, target_year_profit=0.0)
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