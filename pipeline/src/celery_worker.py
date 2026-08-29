from celery_app import app
import portfolio
import pipeline
import makeStats
import os
from logger_setup import get_logger

logger = get_logger(__name__)

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

def build_tasks(
		listTimeFrame: list = ["8min", "18min", "36min", "48min"],
		mode: str = "imitation"
	) -> list:

	listPortfolio = [
		"standart",
	]

	testMode = "reinvest" #cumul/reinvest
	portfolioMode = "reinvest" #cumul/reinvest

	listTimeFrame = [
		"4h",
#		"3h",
#		"2h",
#		"1h",
#		"48min",
#		"45min",
#		"36min",
#		"30min",
#		"24min",
#		"20min",
#		"15min",
	]
	listSymbol = [
		"BTC",
		"ETH",
		"BNB",
		"SOL",
		"ADA",
		"ZEC",
		"DOGE",
		"SUI",
		"NEAR",
		"AVAX",
		"FIL",
		"XRP",

#		"TRX",
#		"BCH",
#		"LINK",
#		"XMR",
#		"LTC",
#		"HYPE",
#		"RE",
#		"BOT",
#		"LYTE",
	]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']
	listStrategy = [
		"opt_cross_ma:I",
		"opt_cross_kama:I",
		"opt_cross_hama:I",
		"opt_cross_ema:I",
		"opt_cross_curve:I",
		"opt_trend:I",
		"opt_stochastic:I",
		"opt_bollinger:I",
		"opt_keltner:I",
		"opt_envelopes:I",
		"opt_modeling:I",

#		"opt_lrcurve:I",
#		"opt_moving:I",
#		"opt_kama:I",
#		"opt_hama:I",
#		"opt_ema:I",
#		"opt_lrchannel:I",
#		"opt_correlation:II",
#		"hold:N",
	]
	listFactor = [
		"BTC",
#		"ETH",
#		"BNB"
#		"RE",
#		"BOT",
	]
	listTypeFactor = ["futures"]
	listFactorExchange = ["binance"]

	portfolioList = []
	for portfolioName in listPortfolio:

		assetsList = []
		for nameExchange in listNameExchange:
			for typeMarket in listTypeMarket:
				for strategy in listStrategy:
					for symbol in listSymbol:
						splitNameStrategy = strategy.split(":")

						if (splitNameStrategy[1] == "N"):
							if mode == 'portfolio':
								assetsList.append({
									'mode': mode,
									'testMode': testMode,
									'nameExchange': nameExchange,
									'symbol': symbol,
									'type': typeMarket,
									'timeFrame': '1d',
									'strategy': strategy,
									'factor': 'None',
									'typeFactor': 'None',
									'factorExchange': 'None'
								})

						else:
							for timeFrame in listTimeFrame:

								if splitNameStrategy[1] == "I":
									assetsList.append({
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
													assetsList.append({
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

		portfolioList.append(
			{
				'portfolioName': portfolioName,
				'portfolioMode': portfolioMode,
				'assetsList': assetsList,
			}
		)

	tasks_to_run: list = []
	if mode == 'portfolio':
		for i in range(len(portfolioList)):
			assetsList = portfolioList[i]['assetsList']
			lenthCombi = len(assetsList)
			logger.info(f"full lenth combination = {lenthCombi}")

			tasks_to_run.append({'id': i+1, 'mode': mode, 'params': portfolioList[i]})

	elif mode == 'test':
		for i in range(len(portfolioList)):
			portfolioName = portfolioList[i]['portfolioName']
			assetsList = portfolioList[i]['assetsList']
			
			lenthCombi = len(assetsList)
			logger.info(f" portfolio {portfolioName}: full lenth combination = {lenthCombi}")

			for i in range(len(assetsList)):
				tasks_to_run.append({'id': i+1, 'mode': mode, 'params': assetsList[i]})

	elif mode == 'stats':
		makeStats.main(
			listTimeFrame=listTimeFrame,
			listStrategy=listStrategy,
			listSymbol=listSymbol,
			listFactor=listFactor,
		)

	return tasks_to_run

@app.task
def run_workflow(timeframe: str) -> str:
	logger.info(f"🔄 pipeline_work создает задачи для {timeframe}")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		app.send_task(
			'celery_worker.run_portfolio',
			args=[task['id'], task['mode'], task['params']],
			queue='pipeline_work'
		)
	logger.info(f"✅ pipeline_work заготовил себе {len(tasks)} задач для {timeframe}")
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

@app.task
def run_portfolio(item_id: int, mode: str, params: dict) -> None:
	logger.info(f"🚀 Worker выполняет задачу {item_id}")
	try:
		if mode == 'portfolio':
			portfolio.main(params)
		elif mode == 'test':
			pipeline.main(params)
		logger.info(f"✅ Задача {item_id} завершена!")
	except Exception as e:
		logger.error(f"❌ Ошибка в задаче {item_id}: {e}")
		raise

if global_work_mode in ['portfolio', 'test', 'stats']:
	def startBackTests() -> None:
		logger.info(f"Пользователь создает задачи для бэктеста!")
		tasks = build_tasks(mode=global_work_mode)
		for task in tasks:
			app.send_task(
				'celery_worker.run_portfolio',
				args=[task['id'], task['mode'], task['params']],
				queue='pipeline_work'
			)
		logger.info(f"✅ Пользователь отправил {len(tasks)} задач!")

	startBackTests()

elif global_work_mode == 'imitation':
	pass
