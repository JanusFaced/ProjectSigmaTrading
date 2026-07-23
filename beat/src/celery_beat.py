from celery_app import app
from datetime import timedelta
import os

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

if global_work_mode == 'imitation':
    app.conf.beat_schedule = {
        'parser-cycle-1min': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=1),
            'kwargs': {},
            'options': {'queue': 'pipeline_parser'},
        },
        'work-cycle-8min': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=8),
            'kwargs': {'timeframe': '8min'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-18min': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=18),
            'kwargs': {'timeframe': '18min'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-36min': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=36),
            'kwargs': {'timeframe': '36min'},
            'options': {'queue': 'pipeline_work'},
        },
        'work-cycle-48min': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=48),
            'kwargs': {'timeframe': '48min'},
            'options': {'queue': 'pipeline_work'},
        }
    }