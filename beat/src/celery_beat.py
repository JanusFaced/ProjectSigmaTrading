from celery_app import app
from datetime import timedelta
import os

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

if global_work_mode == 'imitation':
    app.conf.beat_schedule = {
        'work-cycle-1h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=60),
            'kwargs': {'timeframe': '1h'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-2h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=120),
            'kwargs': {'timeframe': '2h'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-3h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=180),
            'kwargs': {'timeframe': '3h'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-4h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=240),
            'kwargs': {'timeframe': '4h'},
            'options': {'queue': 'pipeline_work'},
        }
    }