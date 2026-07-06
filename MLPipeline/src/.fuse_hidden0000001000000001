from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import os
import sys
import time
import pipeline
import filters
from logger_setup import get_logger

logger = get_logger(__name__)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('MLPipeline', broker=REDIS_URL)

app.conf.update(
	task_serializer='json',
	accept_content=['json'],
	result_serializer='json',
	timezone='UTC',
	task_default_queue='default',
	task_queues={
		'high_priority': {
			'exchange': 'high_priority',
			'routing_key': 'high_priority',
		},
		'medium_priority': {
			'exchange': 'medium_priority',
			'routing_key': 'medium_priority',
		},
		'low_priority': {
			'exchange': 'low_priority',
			'routing_key': 'low_priority',
		},
	},
	task_routes={
		'tasks.scheduled_run_8min': {'queue': 'high_priority'},
		'tasks.scheduled_run_18min': {'queue': 'medium_priority'},
		'tasks.scheduled_run_36min': {'queue': 'medium_priority'},
		'tasks.scheduled_run_48min': {'queue': 'low_priority'},
	}
)

@app.task
def run_pipeline(item_id: int, params: dict) -> None:
	logger.info(f"Запуск задачи {item_id} с параметрами: {params}")
	pipeline.main(params)
	logger.info(f"Задача {item_id} завершена!")

@app.task
def build_tasks(listTimeFrame: list) -> list:

	mode = 'imitation'
	testMode = 'cumul'
	target_year_profit = 30.0

	listNameExchange = ['binance']
	listTypeMarket = ['futures']
	listSymbol = ['ETH', 'BNB', 'SOL', 'TRX', 'ADA']
	listStrategy = ['moving', 'channel', 'forecast', 'modeling']

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

	if mode == "imitation":
		listMSGs = filters.forImitation(
			listMSGs=listMSGs,
			target_year_profit=target_year_profit,
			modeFilter='exist'
		)
		lenthCombi = len(listMSGs)
		logger.info(f"filter for imitation lenth combination = {lenthCombi}")

	tasks_to_run: list = []
	for i in range(len(listMSGs)):
		tasks_to_run.append({'id': i+1, 'params': listMSGs[i]})

	return tasks_to_run

@app.task
def scheduled_run_8min(timeframe: str) -> str:
	logger.info("🔴 [HIGH] Запуск по расписанию для 8min!")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		run_pipeline.delay(task['id'], task['params'])
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

@app.task
def scheduled_run_18min(timeframe: str) -> str:
	logger.info("🟡 [MEDIUM] Запуск по расписанию для 18min!")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		run_pipeline.delay(task['id'], task['params'])
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

@app.task
def scheduled_run_36min(timeframe: str) -> str:
	logger.info("🟡 [MEDIUM] Запуск по расписанию для 36min!")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		run_pipeline.delay(task['id'], task['params'])
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

@app.task
def scheduled_run_48min(timeframe: str) -> str:
	logger.info("🟢 [LOW] Запуск по расписанию для 48min!")
	tasks = build_tasks(listTimeFrame=[timeframe])
	for task in tasks:
		run_pipeline.delay(task['id'], task['params'])
	return f"Scheduled {len(tasks)} tasks for {timeframe}"

app.conf.beat_schedule = {
	'run-work-cycle-8min': {
		'task': 'tasks.scheduled_run_8min',
		'schedule': timedelta(minutes=8),
		'kwargs': {'timeframe': '8min'}
	},
	'run-work-cycle-18min': {
		'task': 'tasks.scheduled_run_18min',
		'schedule': timedelta(minutes=18),
		'kwargs': {'timeframe': '18min'}
	},
	'run-work-cycle-36min': {
		'task': 'tasks.scheduled_run_36min',
		'schedule': timedelta(minutes=36),
		'kwargs': {'timeframe': '36min'}
	},
	'run-work-cycle-48min': {
		'task': 'tasks.scheduled_run_48min',
		'schedule': timedelta(minutes=48),
		'kwargs': {'timeframe': '48min'}
	}
}