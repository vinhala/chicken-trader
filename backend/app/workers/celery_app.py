from celery import Celery

from app.core.config import settings


celery = Celery("investment_app", broker=settings.redis_url, backend=settings.redis_url, include=["app.workers.tasks"])
celery.conf.beat_schedule = {
    "ingest-news-every-6h": {"task": "app.workers.tasks.ingest_news_task", "schedule": 21600},
    "reevaluate-theses-daily": {"task": "app.workers.tasks.reevaluate_theses_task", "schedule": 86400},
}
celery.conf.timezone = "UTC"
celery.conf.broker_connection_retry_on_startup = True
