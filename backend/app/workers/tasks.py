from app.db.base import SessionLocal
from app.models.entities import Event
from app.services.ai import generate_report_for_event
from app.services.news import ingest_news
from app.services.thesis import reevaluate_active_theses
from app.workers.celery_app import celery


@celery.task
def ingest_news_task() -> dict:
    db = SessionLocal()
    try:
        inserted = ingest_news(db)
        events = db.query(Event).order_by(Event.created_at.desc()).limit(10).all()
        for event in events:
            generate_report_for_event(db, event)
        return {"inserted": inserted}
    finally:
        db.close()


@celery.task
def reevaluate_theses_task() -> dict:
    db = SessionLocal()
    try:
        evaluated = reevaluate_active_theses(db)
        return {"evaluated": evaluated}
    finally:
        db.close()
