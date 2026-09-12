from celery_app import app
import portfolio
import pipeline
import portfolio_controller
from filters_kit import filter_exist, filter_new
import os
from logger_setup import get_logger

logger = get_logger(__name__)

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

def build_tasks(
		listTimeFrame: list = ["4h"],
		mode: str = "imitation"
	) -> list:

	validMetrics = {
		"target_year_profit": -100.0,
		"target_max_drawdown": -100.0,
		"target_sharp": -100.0,
	}

	listPortfolio = ["standart"]

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
	]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']
	listStrategy = [
		"trend_range_fractal:I",
		"trend_envelopes:I",
		"trend_cross_hama:I",

#		"corr_pirson:II",
#		"hold:N",
	]
	listFactor = [
		"BTC",
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

		portfolioList.append({
			'portfolioName': portfolioName,
			'portfolioMode': portfolioMode,
			'commonMode': mode,
			'listTimeFrame': listTimeFrame,
			'listStrategy': listStrategy,
			'listSymbol': listSymbol,
			'listFactor': listFactor,
			'assetsList': assetsList,
		})

	tasks_to_run: list = []
	if mode in ['portfolio', 'valid']:

		assetsList = portfolioList[0]['assetsList']
		listStrategy = portfolioList[0]['listStrategy']
		
		lenthCombi = len(assetsList)
		logger.info(f" * Full lenth combination = {lenthCombi}")

		if not("hold:N" in listStrategy):
			modeSave = True if (mode == 'valid') else False

			assetsList = filter_new.main(
				listMSGs=assetsList,
				validMetrics=validMetrics,
				save=modeSave
			)

		lenthCombi = len(assetsList)
		logger.info(f" * After filters lenth combination = {lenthCombi}")

		portfolioList[0]['assetsList'] = assetsList

		tasks_to_run.append({'id': 1, 'mode': mode, 'params': portfolioList[0]})

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
		if mode in ['portfolio', 'valid']:
			portfolio.main(params)
		elif mode in ['test', 'imitation', 'real']:
			pipeline.main(params)
		logger.info(f"✅ Задача {item_id} завершена!")
	except Exception as e:
		logger.error(f"❌ Ошибка в задаче {item_id}: {e}")
		raise

@app.task
def run_controller() -> str:
	logger.info(f"🔄 pipeline_work создает задачу для run_controller")
	app.send_task(
		'celery_worker.run_portfolio_controller',
		args=[],
		queue='pipeline_work'
	)
	logger.info(f"✅ pipeline_work заготовил себе задачу для run_controller")
	return f"Scheduled 1 task for run_controller"

@app.task
def run_portfolio_controller() -> None:
	logger.info(f"🚀 Worker выполняет задачу run_portfolio_controller!!!")
	try:
		portfolio_controller.main()
		logger.info(f"✅ Задача run_portfolio_controller завершена!")
	except Exception as e:
		logger.error(f"❌ Ошибка в задаче run_portfolio_controller: {e}")
		raise

if global_work_mode in ['portfolio', 'test', 'valid']:
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
	
	'''
	def deleteTable():

		from sqlalchemy import create_engine, text

		dataBase_password = os.getenv('DB_PASSWORD')
		dataBase_user = os.getenv('DB_USER')
		dataBase_name = os.getenv('DB_NAME')
		dataBase_host = os.getenv('DB_HOST')
		dataBase_port = os.getenv('DB_PORT')

		DATABASE_URL = f"postgresql://{dataBase_user}:{dataBase_password}@{dataBase_host}:{dataBase_port}/{dataBase_name}"

		TABLES = [
			#"short_binance_sol_futures",
			#"short_binance_avax_futures",
			#"short_binance_doge_futures",
			#"short_binance_vet_futures",
			#"short_binance_ada_futures",
			#"short_binance_eth_futures",
			#"short_binance_bnb_futures",
			#"short_binance_zec_futures",
			#"short_binance_btc_futures",
			#"short_binance_xrp_futures",
			#"short_binance_fil_futures",

		]

		engine = create_engine(DATABASE_URL, echo=False)

		stmt = f"TRUNCATE TABLE {', '.join(TABLES)} RESTART IDENTITY"

		with engine.begin() as conn:
			print(f"Executing: {stmt}")
			conn.execute(text(stmt))

			for t in TABLES:
				count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one()
				print(f"  {t}: {count} rows")

		print("Done.")	

	def startImitation() -> None:
		logger.info(f"Пользователь создает задачи для имитации!")
		tasks = build_tasks(listTimeFrame = ['4h'], mode=global_work_mode)
		for task in tasks:
			app.send_task(
				'celery_worker.run_portfolio',
				args=[task['id'], task['mode'], task['params']],
				queue='pipeline_work'
			)
		logger.info(f"✅ Пользователь отправил {len(tasks)} задач!")
	
	'''
	
	#startImitation()

	#portfolio_controller.main()

	pass
