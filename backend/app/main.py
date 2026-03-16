import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api import auth, broker, notifications, opportunities, theses, watchlist
from app.db.base import Base, SessionLocal, engine
from app.models import entities  # noqa: F401

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Investment Opportunity MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    for attempt in range(1, 11):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            if attempt == 10:
                raise
            logger.warning("Database not ready (attempt %d/10), retrying in 3s...", attempt)
            time.sleep(3)

    # Trigger an immediate news ingest if the database has no events yet,
    # so the app has data on first boot instead of waiting up to 6 hours for Celery Beat.
    db = SessionLocal()
    try:
        from app.models.entities import Event
        if not db.query(Event).first():
            logger.warning("No events found on startup, triggering initial news ingest")
            from app.workers.tasks import ingest_news_task
            ingest_news_task.delay()
    finally:
        db.close()


app.include_router(auth.router, prefix="/api")
app.include_router(opportunities.router, prefix="/api")
app.include_router(theses.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(broker.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
