from celery import Celery
from config import settings

celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.tasks.tasks", "src.celery_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=3600,
)

celery_app.conf.beat_schedule = {
    # Add random task every minute
    'add-random-task-every-minute': {
        'task': 'tasks.tasks.periodic_add_random_task',
        'schedule': 86400.0,  # Run every 86400 seconds (24 hours / everyday)
    },

    # Example periodic task (commented out)
    'periodic-task': {
        'task': 'celery_tasks.example_task',
        'schedule': 30.0,  # Run every 30 seconds
    },
}

if __name__ == '__main__':
    celery_app.start()