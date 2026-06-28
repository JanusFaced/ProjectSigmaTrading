from typing import Any
import dataFrameDownloader
from strategies import moving
from strategies import channel
from strategies import oscillator
from strategies import cross
from strategies import trend
from strategies import stoploss
from strategies import lr_channel
from strategies import lr_stoploss
from strategies import lr_curve
from strategies import modeling_curve
from strategies import modeling_channel
from strategies import modeling_stoploss
from strategies import smooth_modeling_close
from strategies import lr_modeling_close
from strategies import lr_modeling_ind
from strategies import lr_modeling_channel
from strategies import forest_modeling_ind
from strategies import forest_modeling_close_w
from strategies import forest_modeling_close_i
from strategies import boost_modeling_ind
from strategies import boost_modeling_close_w
from strategies import boost_modeling_close_i
from strategies import logreg_class
from strategies import tree_class
from strategies import forest_class
from strategies import boost_class
import trading_simulator
import imitation_connector
from logger_setup import get_logger

logger = get_logger(__name__)

def main(inputMessage: dict[str, Any]) -> None:
	dataFrame: pd.DataFrame = dataFrameDownloader.main(inputMessage)

	if inputMessage["strategy"] == "moving":
		dataFrame = moving.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "channel":
		dataFrame = channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "oscillator":
		dataFrame = oscillator.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "cross":
		dataFrame = cross.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "trend":
		dataFrame = trend.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "stoploss":
		dataFrame = stoploss.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_channel":
		dataFrame = lr_channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_stoploss":
		dataFrame = lr_stoploss.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_curve":
		dataFrame = lr_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_curve":
		dataFrame = modeling_curve.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_channel":
		dataFrame = modeling_channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "modeling_stoploss":
		dataFrame = modeling_stoploss.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "smooth_modeling_close":
		dataFrame = smooth_modeling_close.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_close":
		dataFrame = lr_modeling_close.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_ind":
		dataFrame = lr_modeling_ind.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "lr_modeling_channel":
		dataFrame = lr_modeling_channel.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "forest_modeling_ind":
		dataFrame = forest_modeling_ind.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "forest_modeling_close_w":
		dataFrame = forest_modeling_close_w.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "forest_modeling_close_i":
		dataFrame = forest_modeling_close_w.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "boost_modeling_ind":
		dataFrame = boost_modeling_ind.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "boost_modeling_close_w":
		dataFrame = boost_modeling_close_w.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "boost_modeling_close_i":
		dataFrame = boost_modeling_close_i.main(inputMessage, dataFrame)
	elif inputMessage["strategy"] == "logreg_class":
		dataFrame = logreg_class.main(inputMessage, dataFrame)
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

	listMSGs = [
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '1min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '2min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '4min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '8min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '15min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '30min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '1h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '2h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '4h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '6h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '8h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '12h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BTC', 'type': 'futures', 'timeFrame': '1d', 'strategy': 'moving'},

		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '1min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '2min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '4min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '8min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '15min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '30min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '1h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '2h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '4h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '6h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '8h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '12h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'ETH', 'type': 'futures', 'timeFrame': '1d', 'strategy': 'moving'},

		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '1min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '2min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '4min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '8min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '15min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '30min', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '1h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '2h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '4h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '6h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '8h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '12h', 'strategy': 'moving'},
		{'mode': 'test', 'nameExchange': 'binance', 'symbol': 'BNB', 'type': 'futures', 'timeFrame': '1d', 'strategy': 'moving'},

	]

	for msg in listMSGs:
		main(msg)