import logging

from app.db.base import SessionLocal
from app.models.entities import Event
from app.services.ai import generate_report_for_event
from app.services.news import ingest_news
from app.services.thesis import reevaluate_active_theses
from app.workers.celery_app import celery

logger = logging.getLogger(__name__)


@celery.task
def ingest_news_task() -> dict:
    db = SessionLocal()
    try:
        inserted = ingest_news(db)
        events = db.query(Event).order_by(Event.created_at.desc()).limit(10).all()
        for event in events:
            generate_report_for_event(db, event)
        return {"inserted": inserted}
    except Exception as exc:
        logger.warning("ingest_news_task failed: %s", exc)
        raise
    finally:
        db.close()


@celery.task
def reevaluate_theses_task() -> dict:
    db = SessionLocal()
    try:
        evaluated = reevaluate_active_theses(db)
        return {"evaluated": evaluated}
    except Exception as exc:
        logger.warning("reevaluate_theses_task failed: %s", exc)
        raise
    finally:
        db.close()
