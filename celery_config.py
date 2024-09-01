from celery import Celery
import os

# Retrieve Redis URL from environment variables or use a default value
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app_name=__name__):
    # Create and configure Celery application
    celery = Celery(app_name, broker=REDIS_URL, backend=REDIS_URL)

    celery.conf.update(
        result_expires=3600,
        worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
        worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(task_name)s - %(message)s'
    )

    return celery

celery_app = make_celery()

# Import task module to ensure tasks are registered
import tasks
