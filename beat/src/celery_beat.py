from celery_app import app
from datetime import timedelta
import os

global_work_mode = os.getenv('GLOBAL_WORK_MODE')

if global_work_mode == 'imitation':

    app.conf.beat_schedule = {
        'work-cycle-portfolio-controller': {
            'task': 'celery_worker.run_controller',
            'schedule': timedelta(minutes=17),
            'kwargs': {},
            'options': {'queue': 'pipeline_work'},
        },
#        'work-cycle-test': {
#            'task': 'celery_worker.run_workflow',
#            'schedule': timedelta(minutes=10),
#            'kwargs': {'timeframe': '4h'},
#            'options': {'queue': 'pipeline_work'},
#        },
        'work-cycle-4h': {
            'task': 'celery_worker.run_workflow',
            'schedule': timedelta(minutes=240),
            'kwargs': {'timeframe': '4h'},
            'options': {'queue': 'pipeline_work'},
        },
    }