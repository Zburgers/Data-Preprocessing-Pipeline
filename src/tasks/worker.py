from celery import Celery
from celery.schedules import crontab
import os
import time
from contextlib import contextmanager

from src.utils.config import settings
from src.utils.logging import logger

# Create Celery application
app = Celery("preprocessing_pipeline")

# Configure Celery
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"
app.conf.enable_utc = True
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_track_started = True

# Define task queues
app.conf.task_routes = {
    "src.tasks.dataset_tasks.*": {"queue": "dataset"},
    "src.tasks.pipeline_tasks.*": {"queue": "pipeline"},
    "src.tasks.export_tasks.*": {"queue": "export"},
    "src.tasks.detection_tasks.*": {"queue": "detection"},
    "src.tasks.scheduled_tasks.*": {"queue": "scheduled"},
}

# Define periodic tasks
app.conf.beat_schedule = {
    "cleanup-temp-files": {
        "task": "src.tasks.scheduled_tasks.cleanup_temp_files",
        "schedule": crontab(hour=3, minute=0),  # Run at 3:00 AM
    },
    "check-stalled-jobs": {
        "task": "src.tasks.scheduled_tasks.check_stalled_jobs",
        "schedule": crontab(minute="*/15"),  # Run every 15 minutes
    },
}

# Auto-discover tasks from these modules
app.autodiscover_tasks(["src.tasks.dataset_tasks", 
                         "src.tasks.pipeline_tasks", 
                         "src.tasks.export_tasks",
                         "src.tasks.detection_tasks",
                         "src.tasks.scheduled_tasks"])

@contextmanager
def task_context(task_name: str):
    """
    Context manager for task execution with logging and error handling.
    
    Args:
        task_name: The name of the task
    """
    start_time = time.time()
    logger.info(f"Starting task: {task_name}")
    try:
        yield
        execution_time = time.time() - start_time
        logger.info(f"Task {task_name} completed in {execution_time:.2f}s")
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Task {task_name} failed after {execution_time:.2f}s: {str(e)}")
        raise

if __name__ == "__main__":
    app.start() 