from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, broker, notifications, opportunities, theses, watchlist
from app.db.base import Base, SessionLocal, engine
from app.models import entities  # noqa: F401
from app.models.entities import BrokerInstrument, Event
from app.services.ai import generate_report_for_event
from app.services.news import ingest_news


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
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ingest_news(db)
        for event in db.query(Event).order_by(Event.created_at.desc()).limit(20).all():
            generate_report_for_event(db, event)
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
