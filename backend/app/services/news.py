import hashlib
import logging
import re
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Article, Event

logger = logging.getLogger(__name__)

# Common English stopwords to ignore when clustering by keyword overlap
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "will", "would", "could", "should", "may", "might",
    "its", "it", "this", "that", "as", "up", "over", "into", "out", "new",
    "after", "amid", "than", "more", "less", "report", "says", "said",
    "amid", "amid", "amid", "about", "after", "again", "against", "all",
    "also", "amid", "amid",
}


def _dedupe_hash(source: str, title: str, url: str) -> str:
    return hashlib.sha256(f"{source}|{title}|{url}".encode("utf-8")).hexdigest()


def _extract_keywords(text: str) -> set[str]:
    """Strips stopwords and punctuation; returns meaningful words for clustering."""
    words = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


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
        "tariff": 14,
        "inflation": 16,
        "gdp": 15,
        "ipo": 16,
        "bankruptcy": 14,
    }
    for key, points in keywords.items():
        if key in text:
            score += points
    return min(score, 100)


def _cluster_event(db: Session, title: str) -> Optional[Event]:
    """Find an existing event that shares meaningful keywords with this article title."""
    keywords = _extract_keywords(title)
    if not keywords:
        return None
    candidates = db.query(Event).order_by(Event.created_at.desc()).limit(50).all()
    for event in candidates:
        shared = keywords & _extract_keywords(event.headline)
        # Require at least 2 shared meaningful words for clustering
        if len(shared) >= 2:
            return event
    return None


def fetch_news() -> list[dict]:
    if not settings.news_api_key:
        logger.warning("NEWS_API_KEY not configured, returning demo articles")
        return [
            {
                "source": "demo",
                "title": "Central bank signals slower rate cuts amid persistent inflation",
                "url": "https://example.com/news/central-bank-rate-cuts",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "Markets reprice growth and duration-sensitive assets as policymakers signal a more cautious easing path.",
            },
            {
                "source": "demo",
                "title": "Semiconductor export restrictions tighten on advanced chips",
                "url": "https://example.com/news/semiconductor-export-controls",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "New rules target advanced chip exports, with potential impact on hardware and supply chain names.",
            },
            {
                "source": "demo",
                "title": "Major merger announced in energy sector as oil prices surge",
                "url": "https://example.com/news/energy-merger",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "Two major oil producers announce merger, consolidating market share amid rising commodity prices.",
            },
            {
                "source": "demo",
                "title": "Geopolitical tensions escalate, affecting global supply chains",
                "url": "https://example.com/news/geopolitics-supply-chain",
                "publishedAt": datetime.utcnow().isoformat(),
                "description": "Rising tensions between major economies create uncertainty for manufacturing and logistics stocks.",
            },
        ]

    results: list[dict] = []
    # Fetch across multiple financial news categories to satisfy REQ-ING-002
    queries = [
        # Macroeconomics + central bank + rates
        "central bank OR interest rates OR inflation OR monetary policy OR GDP",
        # Corporate events
        "merger OR acquisition OR earnings OR IPO OR bankruptcy",
        # Geopolitics + commodities
        "sanctions OR tariffs OR oil OR commodity OR geopolitics OR supply chain",
        # Technology + regulation
        "semiconductor OR AI regulation OR antitrust OR fintech",
    ]
    with httpx.Client(timeout=15) as client:
        for query in queries:
            try:
                resp = client.get(
                    f"{settings.news_api_base_url}/everything",
                    params={
                        "apiKey": settings.news_api_key,
                        "q": query,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 10,
                    },
                )
                resp.raise_for_status()
                for a in resp.json().get("articles", []):
                    results.append({
                        "source": (a.get("source") or {}).get("name", "unknown"),
                        "title": a.get("title") or "",
                        "url": a.get("url") or "",
                        "publishedAt": a.get("publishedAt") or datetime.utcnow().isoformat(),
                        "description": a.get("description") or "",
                    })
            except Exception as exc:
                logger.warning("NewsAPI query failed for %r: %s", query, exc)
                continue

    # Deduplicate by URL before returning
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for r in results:
        if r["title"] and r["url"] and r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique.append(r)
    return unique


def ingest_news(db: Session) -> int:
    # Import here to avoid circular imports
    from app.services.ai import classify_event

    articles = fetch_news()
    inserted = 0
    for item in articles:
        d_hash = _dedupe_hash(item["source"], item["title"], item["url"])
        if db.query(Article).filter(Article.dedupe_hash == d_hash).first():
            continue

        event = _cluster_event(db, item["title"])
        if event is None:
            # Use AI to classify market impact, sector, and interpretation (REQ-DET-001..004)
            headline = item["title"][:255]
            summary = (item.get("description") or item["title"])[:1000]
            classification = classify_event(headline, summary)

            if classification:
                market_impact = classification.get("market_impact", "Medium")
                # REQ-DET-003: skip Low-impact events
                if market_impact == "Low":
                    # Still store article but don't create an investment event
                    published = item["publishedAt"].replace("Z", "+00:00")
                    if "T" not in published:
                        logger.warning("Unparseable publishedAt %r for article %r, defaulting to utcnow()", item["publishedAt"], item.get("title", ""))
                    article = Article(
                        event_id=None,
                        source=item["source"][:120],
                        title=item["title"][:500],
                        url=item["url"][:1000],
                        dedupe_hash=d_hash,
                        published_at=datetime.fromisoformat(published) if "T" in published else datetime.utcnow(),
                    )
                    db.add(article)
                    inserted += 1
                    continue

                event = Event(
                    headline=headline,
                    summary=summary,
                    market_interpretation=classification.get("market_interpretation", "Potentially market-moving event requiring monitoring."),
                    sector=classification.get("sector", "General"),
                    confidence=classification.get("confidence", "Medium"),
                    relevance_score=_relevance_score(item["title"], item.get("description", "")),
                )
            else:
                # Fallback classification when OpenAI is unavailable
                event = Event(
                    headline=item["title"][:255],
                    summary=summary,
                    market_interpretation="Potentially market-moving event requiring monitoring.",
                    sector=_heuristic_sector(item["title"]),
                    confidence="Medium",
                    relevance_score=_relevance_score(item["title"], item.get("description", "")),
                )
            db.add(event)
            db.flush()

        published = item["publishedAt"].replace("Z", "+00:00")
        if "T" not in published:
            logger.warning("Unparseable publishedAt %r for article %r, defaulting to utcnow()", item["publishedAt"], item.get("title", ""))
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


def _heuristic_sector(title: str) -> str:
    """Simple keyword-based sector fallback when AI is unavailable."""
    t = title.lower()
    if any(k in t for k in ("bank", "rate", "inflation", "fed", "central")):
        return "Macro"
    if any(k in t for k in ("oil", "gas", "energy", "commodity", "opec")):
        return "Energy"
    if any(k in t for k in ("chip", "semiconductor", "ai ", "software", "tech")):
        return "Technology"
    if any(k in t for k in ("pharma", "drug", "fda", "biotech", "health")):
        return "Healthcare"
    if any(k in t for k in ("sanction", "geopolit", "war", "trade")):
        return "Geopolitics"
    if any(k in t for k in ("regulation", "sec ", "antitrust", "law")):
        return "Regulatory"
    return "General"
