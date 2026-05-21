from pathlib import Path
from celery import Celery
from celery.schedules import crontab
import os
import sys
import time
import logging
import make_logger
import pipeline

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

os.environ['LEVEL_CONFIG'] = 'INFO'
os.environ['WAY_TO_LOG_JOURNAL'] = str(current_dir/'logs'/'log_journal.log')
os.environ['WAY_EXTRACT_FILES'] = str(current_dir/'extract_files')

make_logger.make()
logger = logging.getLogger('MLPipeline:tasks')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('MLPipeline', broker=REDIS_URL)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
)

@app.task
def run_pipeline(item_id, params):
    logger.info(f"Запуск задачи {item_id} с параметрами: {params}")
    result = pipeline.main(params)
    logger.info(f"Задача {item_id} завершена: {result}")
    return result

@app.task
def scheduled_run():
    logger.info("Запуск по расписанию!")

    tasks_to_run = [
        {'id': 1, 'params': {'symbol': 'BTC', 'timeFrame': '1d'}},
        #{'id': 2, 'params': {'symbol': 'ETH', 'timeFrame': '1d'}},
        #{'id': 3, 'params': {'symbol': 'BNB', 'timeFrame': '1d'}},
        #{'id': 4, 'params': {'symbol': 'BTC', 'timeFrame': '1h'}},
        #{'id': 5, 'params': {'symbol': 'ETH', 'timeFrame': '1h'}},
        #{'id': 6, 'params': {'symbol': 'BNB', 'timeFrame': '1h'}},
    ]

    for task in tasks_to_run:
        run_pipeline.delay(task['id'], task['params'])
        logger.info(f"Запланирована задача {task['id']} для {task['params']['symbol']}")

    return f"Scheduled {len(tasks_to_run)} tasks"

app.conf.beat_schedule = {
    'run-every-5-minutes': {
        'task': 'tasks.scheduled_run',
        'schedule': crontab(minute='*/5')
    }
}