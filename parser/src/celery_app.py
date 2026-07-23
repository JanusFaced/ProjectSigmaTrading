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
		'pipeline_parser': {
			'exchange': 'pipeline_parser',
			'routing_key': 'pipeline_parser',
		},
		'pipeline_work': {
			'exchange': 'pipeline_work',
			'routing_key': 'pipeline_work',
		},
	}
)