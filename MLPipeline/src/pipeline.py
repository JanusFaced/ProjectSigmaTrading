from typing import Any
import dataFrameDownloader
from strategies import moving
from strategies import oscillator
from strategies import cross
from strategies import trend
from strategies import stoploss
from strategies import lr_stoploss
from strategies import lr_curve
from strategies import modeling_curve
from strategies import modeling_stoploss
from strategies import smooth_modeling_close
from strategies import lr_modeling_close
from strategies import lr_modeling_ind
from strategies import lr_modeling_channel
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
	elif inputMessage["strategy"] == "oscillator":
		dataFrame = oscillator.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "cross":
		dataFrame = cross.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "trend":
		dataFrame = trend.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "stoploss":
		dataFrame = stoploss.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_stoploss":
		dataFrame = lr_stoploss.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_curve":
		dataFrame = lr_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_curve":
		dataFrame = modeling_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_stoploss":
		dataFrame = modeling_stoploss.main(inputMessage, dataFrame)

	#__rollingML__
	elif inputMessage["strategy"] == "smooth_modeling_close":
		dataFrame = smooth_modeling_close.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_close":
		dataFrame = lr_modeling_close.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_ind":
		dataFrame = lr_modeling_ind.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_channel":
		dataFrame = lr_modeling_channel.main(inputMessage, dataFrame)

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

	mode = 'test'

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
		'oscillator',
		'cross',
		'trend',
		'stoploss',
		'lr_stoploss',
		'lr_curve',
		'modeling_curve',
		'modeling_stoploss',
		'smooth_modeling_close',
		'lr_modeling_close',
		'lr_modeling_ind',
		'lr_modeling_channel',
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
		filters.makeStats(listTimeFrame=listTimeFrame, listStrategy=listStrategy)