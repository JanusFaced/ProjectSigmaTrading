from celery_app import app
import downloadHistory
import os
from logger_setup import get_logger

logger = get_logger(__name__)

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

def build_tasks(mode: str = 'imitation') -> list:

	listSymbol = ['ETH', 'BNB', 'SOL', 'TRX', 'ADA',]
	listTypeMarket = ['futures']
	listNameExchange = ['binance']

	listFactor = ['BTC']
	listTypeFactor = ['futures']
	listFactorExchange = ['binance']

	listMSGs = []
	for nameExchange in listNameExchange:
		for typeMarket in listTypeMarket:
			for symbol in listSymbol:
				listMSGs.append({
						'mode': mode,
						'nameExchange': nameExchange,
						'symbol': symbol,
						'type': typeMarket,
					})

	for nameExchange in listFactorExchange:
		for typeMarket in listTypeFactor:
			for symbol in listFactor:
				listMSGs.append({
						'mode': mode,
						'nameExchange': nameExchange,
						'symbol': symbol,
						'type': typeMarket,
					})

	lenthCombi = len(listMSGs)
	logger.info(f"full lenth combination = {lenthCombi}")

	tasks_to_run: list = []
	if mode != 'stats':
		for i in range(len(listMSGs)):
			tasks_to_run.append({'id': i+1, 'params': listMSGs[i]})

	return tasks_to_run

@app.task
def run_workflow() -> str:
	logger.info(f"🔄 pipeline_parser создает задачи!")
	tasks = build_tasks()
	for task in tasks:
		app.send_task(
			'celery_worker.run_pipeline',
			args=[task['id'], task['params']],
			queue='pipeline_parser'
		)
	logger.info(f"✅ pipeline_parser заготовил {len(tasks)} задач!")
	return f"Scheduled {len(tasks)} tasks"

@app.task
def run_pipeline(item_id: int, params: dict) -> None:
	logger.info(f"🚀 Worker выполняет задачу {item_id}")
	try:
		downloadHistory.main(
			nameExchange=params['nameExchange'],
			symbol=params['symbol'],
			type=params['type'],
			mode=params['mode'],
		)
		logger.info(f"✅ Задача {item_id} завершена!")
	except Exception as e:
		logger.error(f"❌ Ошибка в задаче {item_id}: {e}")
		raise

if global_work_mode in ['test']:
	def startBackTests() -> None:
		logger.info(f"Пользователь создает задачи для бэктеста!")
		tasks = build_tasks(mode=global_work_mode)
		for task in tasks:
			app.send_task(
				'celery_worker.run_pipeline',
				args=[task['id'], task['params']],
				queue='pipeline_parser'
			)
		logger.info(f"✅ Пользователь отправил {len(tasks)} задач!")

	startBackTests()

elif global_work_mode == 'imitation':
	pass
