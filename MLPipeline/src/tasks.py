from typing import TypedDict, Any
from celery import Celery
from celery.schedules import crontab
import os
import sys
import time
import pipeline
from logger_setup import get_logger

logger = get_logger(__name__)

class TaskParams(TypedDict):
    symbol: str
    timeFrame: str

class ScheduledTask(TypedDict):
    id: int
    params: TaskParams

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('MLPipeline', broker=REDIS_URL)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
)

@app.task
def run_pipeline(
        item_id: int,
        params: dict[str, Any]
    ) -> None:

    logger.info(f"Запуск задачи {item_id} с параметрами: {params}")
    pipeline.main(params)
    logger.info(f"Задача {item_id} завершена!")

@app.task
def scheduled_run() -> str:
    logger.info("Запуск по расписанию!")

    tasks_to_run: list[ScheduledTask] = [
        {'id': 1, 'params': {'symbol': 'BTC', 'timeFrame': '15min'}},
        {'id': 2, 'params': {'symbol': 'ETH', 'timeFrame': '15min'}},
        {'id': 3, 'params': {'symbol': 'BNB', 'timeFrame': '15min'}},
        {'id': 4, 'params': {'symbol': 'BTC', 'timeFrame': '1h'}},
        {'id': 5, 'params': {'symbol': 'ETH', 'timeFrame': '1h'}},
        {'id': 6, 'params': {'symbol': 'BNB', 'timeFrame': '1h'}},
        {'id': 7, 'params': {'symbol': 'BTC', 'timeFrame': '4h'}},
        {'id': 8, 'params': {'symbol': 'ETH', 'timeFrame': '4h'}},
        {'id': 9, 'params': {'symbol': 'BNB', 'timeFrame': '4h'}},
    ]

    for task in tasks_to_run:
        run_pipeline.delay(task['id'], task['params'])
        logger.info(f"Запланирована задача {task['id']} для {task['params']['symbol']}")

    return f"Scheduled {len(tasks_to_run)} tasks"

app.conf.beat_schedule = {
    'run-work-cycle': {
        'task': 'tasks.scheduled_run',
        'schedule': crontab(minute='*/5')
    }
}