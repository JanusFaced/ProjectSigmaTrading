from celery_app import app
from datetime import timedelta
from logger_setup import get_logger

logger = get_logger(__name__)

app.conf.beat_schedule = {
    'run-work-cycle-8min': {
        'task': 'celery_worker.run_workflow',
        'schedule': timedelta(minutes=8),
        'kwargs': {'timeframe': '8min', 'priority': 'high_priority'}
    },
    'run-work-cycle-18min': {
        'task': 'celery_worker.run_workflow',
        'schedule': timedelta(minutes=18),
        'kwargs': {'timeframe': '18min', 'priority': 'medium_priority'}
    },
    'run-work-cycle-36min': {
        'task': 'celery_worker.run_workflow',
        'schedule': timedelta(minutes=36),
        'kwargs': {'timeframe': '36min', 'priority': 'medium_priority'}
    },
    'run-work-cycle-48min': {
        'task': 'celery_worker.run_workflow',
        'schedule': timedelta(minutes=48),
        'kwargs': {'timeframe': '48min', 'priority': 'low_priority'}
    }
}