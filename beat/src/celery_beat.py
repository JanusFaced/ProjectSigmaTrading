from celery_app import app
from datetime import timedelta
import os

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

if global_work_mode == 'imitation':
    app.conf.beat_schedule = {
        'work-cycle-4h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=240),
            'kwargs': {'timeframe': '4h'},
            'options': {'queue': 'pipeline_work'},
        }
    }