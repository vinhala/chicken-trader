import hashlib
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Article, Event


def _dedupe_hash(source: str, title: str, url: str) -> str:
    return hashlib.sha256(f"{source}|{title}|{url}".encode("utf-8")).hexdigest()


def _relevance_score(title: str, description: str) -> int:
    text = f"{title} {description}".lower()
    score = 40
    keywords = {
        "central bank": 20,
        "rate": 15,
        "merger": 18,
        "acquisition": 18,
        "geopolitical": 12,
        "sanction": 12,
        "commodity": 10,
        "oil": 10,
        "semiconductor": 15,
        "earnings": 14,
        "regulation": 12,
    }
    for key, points in keywords.items():
        if key in text:
            score += points
    return min(score, 100)


def _cluster_event(db: Session, title: str) -> Optional[Event]:
    title_l = title.lower()
    candidates = db.query(Event).order_by(Event.created_at.desc()).limit(25).all()
    for event in candidates:
        shared = set(title_l.split()) & set(event.headline.lower().split())
        if len(shared) >= 3:
            return event
    return None


def fetch_news() -> list[dict]:
    if not settings.news_api_key:
        return [
            {
                "source": "demo",
                "title": "Central bank signals slower rate cuts",
                "url": "https://example.com/news/central-bank-rate-cuts",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "Markets reprice growth and duration-sensitive assets.",
            },
            {
                "source": "demo",
                "title": "Semiconductor export restrictions tighten",
                "url": "https://example.com/news/semiconductor-export-controls",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "Potential impact on hardware supply chain names.",
            },
        ]

    with httpx.Client(timeout=15) as client:
        resp = client.get(
            f"{settings.news_api_base_url}/top-headlines",
            params={"apiKey": settings.news_api_key, "category": "business", "language": "en", "pageSize": 20},
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for a in data.get("articles", []):
        results.append(
            {
                "source": (a.get("source") or {}).get("name", "unknown"),
                "title": a.get("title") or "",
                "url": a.get("url") or "",
                "publishedAt": a.get("publishedAt") or datetime.utcnow().isoformat(),
                "description": a.get("description") or "",
            }
        )
    return [r for r in results if r["title"] and r["url"]]


def ingest_news(db: Session) -> int:
    articles = fetch_news()
    inserted = 0
    for item in articles:
        d_hash = _dedupe_hash(item["source"], item["title"], item["url"])
        if db.query(Article).filter(Article.dedupe_hash == d_hash).first():
            continue

        event = _cluster_event(db, item["title"])
        if event is None:
            event = Event(
                headline=item["title"][:255],
                summary=(item.get("description") or item["title"])[:1000],
                market_interpretation="Potentially market-moving event requiring monitoring.",
                sector="Macro" if "bank" in item["title"].lower() else "Technology",
                confidence="Medium",
                relevance_score=_relevance_score(item["title"], item.get("description", "")),
            )
            db.add(event)
            db.flush()

        published = item["publishedAt"].replace("Z", "+00:00")
        article = Article(
            event_id=event.id,
            source=item["source"][:120],
            title=item["title"][:500],
            url=item["url"][:1000],
            dedupe_hash=d_hash,
            published_at=datetime.fromisoformat(published) if "T" in published else datetime.utcnow(),
        )
        db.add(article)
        inserted += 1

    db.commit()
    return inserted
