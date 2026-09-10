from celery_app import app
import portfolio
import pipeline
from filters_kit import filter_exist, filter_new
import os
from logger_setup import get_logger

logger = get_logger(__name__)

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

def build_tasks(
		listTimeFrame: list = ["1h", "2h", "3h", "4h"],
		mode: str = "imitation"
	) -> list:

	validMetrics = {
		"target_year_profit": -100.0,
		"target_max_drawdown": -100.0,
		"target_sharp": -100.0,
	}

	listPortfolio = [
		"standart",
	]

	testMode = "reinvest" #cumul/reinvest
	portfolioMode = "reinvest" #cumul/reinvest

	if mode != 'imitation':

		listTimeFrame = [
			"4h",
		]

	listSymbol = [
		"SOL",
		"AVAX",
		"DOGE",
		"VET",
		"ADA",
		"ETH",
		"BNB",
		"ZEC",
		"BTC",
		"XRP",
		"FIL",

#		"NEAR",
#		"DASH",
#		"ALGO",
#		"TRX",
#		"UNI",
#		"BCH",
#		"DOT",
#		"XLM",
#		"ATOM",
#		"LTC",
#		"XMR",
#		"LINK",
#		"SUSHI",
#		"MANA",
#		"SAND",
#		"ICP",
#		"CAKE",
#		"POL",
#		"ARB",
#		"OP",
#		"CRV",
#		"COMP",
#		"CHZ",
#		"SUI",
#		"HYPE",
#		"RE",
#		"BOT",
#		"LYTE",
	]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']
	listStrategy = [
#		"trend_range_fractal:I",
#		"trend_envelopes:I",
#		"trend_cross_hama:I",

#		"corr_pirson:II",
		"hold:N",
	]
	listFactor = [
		"BTC",
		"ETH",
		"BNB"
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
				'listTimeFrame': listTimeFrame,
				'listStrategy': listStrategy,
				'listSymbol': listSymbol,
				'listFactor': listFactor,
				'assetsList': assetsList,
			}
		)

	tasks_to_run: list = []
	if mode == 'portfolio':

		for i in range(len(portfolioList)):
			assetsList = portfolioList[i]['assetsList']
			listStrategy = portfolioList[i]['listStrategy']
			
			lenthCombi = len(assetsList)
			logger.info(f" * Full lenth combination = {lenthCombi}")

			if not("hold:N" in listStrategy):

				assetsList = filter_new.main(
					listMSGs=assetsList,
					validMetrics=validMetrics,
					save=False
				)

			lenthCombi = len(assetsList)
			logger.info(f" * After filters lenth combination = {lenthCombi}")

			portfolioList[i]['assetsList'] = assetsList

			tasks_to_run.append({'id': i+1, 'mode': mode, 'params': portfolioList[i]})

	elif mode in ['test', 'imitation', 'real']:
		for i in range(len(portfolioList)):
			portfolioName = portfolioList[i]['portfolioName']
			assetsList = portfolioList[i]['assetsList']
			
			if mode in ['imitation', 'real']:
				assetsList = filter_exist.main(assetsList)

			lenthCombi = len(assetsList)
			logger.info(f" portfolio {portfolioName}: full lenth combination = {lenthCombi}")

			portfolioList[i]['assetsList'] = assetsList

			for i in range(len(assetsList)):
				tasks_to_run.append({'id': i+1, 'mode': mode, 'params': assetsList[i]})

	elif mode == 'valid':
		assetsList = portfolioList[0]['assetsList']
		
		filter_new.main(
			listMSGs=assetsList,
			validMetrics=validMetrics,
			save=True
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

if global_work_mode in ['portfolio', 'test']:
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
