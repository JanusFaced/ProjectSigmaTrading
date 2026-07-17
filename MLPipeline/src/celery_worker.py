from celery_app import app
import pipeline
from filters_kit import filter_exist
from logger_setup import get_logger

logger = get_logger(__name__)

def build_tasks(listTimeFrame: list) -> list:

	mode = 'imitation'
	testMode = 'cumul'
	target_year_profit = 30.0

	listSymbol = [
		'ETH',
		'BNB',
		'SOL',
		'TRX',
		'ADA',
	]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']
	listStrategy = [
		'moving:I',
		'channel:I',
		'forecast:I',
		'modeling:I',
		'pattern:I',
		'correlation:II'
	]
	listFactor = ['BTC']
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

	if mode == "imitation":
		listMSGs = filter_exist.main(
			listMSGs=listMSGs,
			target_year_profit=target_year_profit
		)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for imitation lenth combination = {lenthCombi}")

	tasks_to_run: list = []
	for i in range(len(listMSGs)):
		tasks_to_run.append({'id': i+1, 'params': listMSGs[i]})

	return tasks_to_run

@app.task
def run_workflow(timeframe: str, priority: str) -> str:
	logger.info(f"🔄 Beat создает задачи для {timeframe}")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		app.send_task(
			'celery_worker.run_pipeline',
			args=[task['id'], task['params']],
			queue=priority
		)
	logger.info(f"✅ Beat отправил {len(tasks)} задач для {timeframe}")
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

@app.task
def run_pipeline(item_id: int, params: dict) -> None:
	logger.info(f"🚀 Worker выполняет задачу {item_id}")
	try:
		pipeline.main(params)
		logger.info(f"✅ Задача {item_id} завершена!")
	except Exception as e:
		logger.error(f"❌ Ошибка в задаче {item_id}: {e}")
		raise
