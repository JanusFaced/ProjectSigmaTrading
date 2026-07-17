from celery import Celery
import os

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
	}
)