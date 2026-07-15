from typing import Any
import dataFrameDownloader
from strategies import moving
from strategies import channel
from strategies import forecast
from strategies import modeling
from strategies import pattern
from strategies import correlation
import trading_simulator
import imitation_connector
import filters
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
	
	dataFrame: pd.DataFrame = dataFrameDownloader.main(
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
		dataFrame = moving.main(inputMessage, dataFrame)
	elif firstName == "channel":
		dataFrame = channel.main(inputMessage, dataFrame)
	elif firstName == "forecast":
		dataFrame = forecast.main(inputMessage, dataFrame)
	elif firstName == "modeling":
		dataFrame = modeling.main(inputMessage, dataFrame)
	elif firstName == "pattern":
		dataFrame = pattern.main(inputMessage, dataFrame)
	elif firstName == "correlation":
		dataFrame = correlation.main(inputMessage, dataFrame)

	if inputMessage['mode'] == 'test':
		trading_simulator.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'imitation':
		imitation_connector.main(inputMessage, dataFrame)
	elif inputMessage['mode'] == 'real':
		pass

if __name__ == "__main__":

	mode = 'imitation'
	testMode = 'cumul'
	target_year_profit = 30.0

	listSymbol = [
#		'BTC',
#		'ETH',
#		'BNB',
#		'XRP',
#		'SOL',
#		'TRX',
#		'HYPE',
#		'ADA',
#		'LINK',
		'RE',
		'BOT',
	]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']
	listTimeFrame = [
		'8min',
#		'18min',
#		'36min',
#		'48min',
	]
	listStrategy = [
		'moving:I',
#		'channel:I',
#		'forecast:I',
#		'modeling:I',
#		'pattern:I',
		'correlation:II'
	]
	listFactor = [
#		'BTC',
		'RE',
		'BOT',
	]
	listTypeFactor = ['futures']
	listFactorExchange = ['binance']

	listMSGs = []
	for nameExchange in listNameExchange:
		for typeMarket in listTypeMarket:
			for timeFrame in listTimeFrame:
				for symbol in listSymbol:
					for strategy in listStrategy:
						splitNameStrategy = strategy.split(":")

						if splitNameStrategy[1] == "I":
							listMSGs.append({
									'mode': mode,
									'testMode': testMode,
									'nameExchange': nameExchange,
									'symbol': symbol,
									'type': typeMarket,
									'timeFrame': timeFrame,
									'strategy': strategy,
									'factor': 'None',
									'typeFactor': 'None',
									'factorExchange': 'None'
								})

						elif splitNameStrategy[1] == "II":
							for factor in listFactor:
								for typeFactor in listTypeFactor:
									for factorExchange in listFactorExchange:

										logicSymbol = True if (symbol == factor) else False
										logicType = True if (typeMarket == typeFactor) else False
										logicExchange = True if (nameExchange == factorExchange) else False

										if not(logicSymbol and logicType and logicExchange):
											listMSGs.append({
												'mode': mode,
												'testMode': testMode,
												'nameExchange': nameExchange,
												'symbol': symbol,
												'type': typeMarket,
												'timeFrame': timeFrame,
												'strategy': strategy,
												'factor': factor,
												'typeFactor': typeFactor,
												'factorExchange': factorExchange
											})

	lenthCombi = len(listMSGs)
	logger.info(f"full lenth combination = {lenthCombi}")

	if mode in ["stats", "imitation"]:
#		listMSGs = filters.forImitation(
#			listMSGs=listMSGs,
#			target_year_profit=target_year_profit,
#			modeFilter='exist'
#		)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for imitation lenth combination = {lenthCombi}")
	elif mode == "real":
		listMSGs = filters.forReal(listMSGs=listMSGs, target_year_profit=target_year_profit)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for real lenth combination = {lenthCombi}")

	if mode != 'stats':
		for msg in listMSGs:
			#try:
			main(msg)
			#except Exception as e:
			#	logger.info(f"error: {e}")

	if mode in ['stats', 'test']:
		filters.makeStats(listSymbol=listSymbol, listTimeFrame=listTimeFrame, listStrategy=listStrategy)