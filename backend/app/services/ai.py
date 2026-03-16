import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import BrokerInstrument, Event, InvestmentReport, ReportAsset
from app.services.market import validate_ticker

logger = logging.getLogger(__name__)

_REPORT_PROMPT = """You are a financial analyst AI. Generate a structured investment report for the following news event.

Event headline: {headline}
Event summary: {summary}

Return a JSON object with exactly these fields:
{{
  "event_summary": "2-4 sentence plain-language explanation of what occurred",
  "market_impact": "explanation of why this event is relevant to financial markets",
  "historical_context": "reference to similar past events or established analyst reasoning, where applicable",
  "thesis_conditions": "comma-separated list of specific conditions that would confirm or invalidate this thesis",
  "risk_factors": "comma-separated specific risks that could invalidate the thesis",
  "confidence_score": "Low or Medium or High",
  "time_horizon": "Short-term or Medium-term or Event-driven",
  "suggested_assets": [
    {{
      "ticker": "TICKER",
      "name": "Company or asset name",
      "asset_type": "Stock or ETF or Commodity or Index",
      "event_relationship": "how this security relates to the event",
      "directional_impact": "Long or Short or Neutral",
      "justification": "1-2 sentence justification for inclusion"
    }}
  ]
}}

Suggest 3-5 tradable securities most directly affected by this event. Return valid JSON only, no markdown."""

_CLASSIFY_PROMPT = """You are a financial news analyst. Classify this news event for investment relevance.

Headline: {headline}
Summary: {summary}

Return a JSON object:
{{
  "market_impact": "Low or Medium or High",
  "sector": "one of: Macro, Technology, Energy, Healthcare, Financial, Consumer, Industrial, Commodities, Geopolitics, Regulatory",
  "confidence": "Low or Medium or High",
  "market_interpretation": "2-3 sentences explaining the investment relevance of this event"
}}

High = immediate, significant market-moving potential. Medium = notable but indirect or uncertain impact. Low = minimal investment relevance.
Return valid JSON only."""


def _call_openai(prompt: str) -> Optional[dict]:
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as exc:
        logger.warning("OpenAI call failed: %s", exc)
        return None


def classify_event(headline: str, summary: str) -> Optional[dict]:
    """Returns {market_impact, sector, confidence, market_interpretation} or None."""
    return _call_openai(_CLASSIFY_PROMPT.format(headline=headline, summary=summary))


def generate_report_for_event(db: Session, event: Event) -> InvestmentReport:
    existing = db.query(InvestmentReport).filter(InvestmentReport.event_id == event.id).first()
    if existing:
        return existing

    ai_data = _call_openai(_REPORT_PROMPT.format(headline=event.headline, summary=event.summary))

    if ai_data:
        report = InvestmentReport(
            event_id=event.id,
            event_summary=ai_data.get("event_summary") or event.summary,
            market_impact=ai_data.get("market_impact") or event.market_interpretation,
            context=ai_data.get("historical_context") or "",
            risk_factors=ai_data.get("risk_factors") or "",
            thesis_conditions=ai_data.get("thesis_conditions") or "",
            confidence_score=ai_data.get("confidence_score") or event.confidence,
        )
        db.add(report)
        db.flush()

        for asset in ai_data.get("suggested_assets") or []:
            ticker = (asset.get("ticker") or "").strip().upper()
            if not ticker:
                continue
            db.add(ReportAsset(
                report_id=report.id,
                ticker=ticker,
                asset_name=asset.get("name") or ticker,
                asset_type=asset.get("asset_type") or "Stock",
                relationship=asset.get("event_relationship") or "",
                direction=asset.get("directional_impact") or "Long",
                justification=asset.get("justification") or "",
            ))
    else:
        # Fallback when OpenAI is unavailable
        logger.warning("OpenAI report generation returned no data for event %d, using static fallback", event.id)
        report = InvestmentReport(
            event_id=event.id,
            event_summary=event.summary,
            market_impact=event.market_interpretation,
            context="Comparable events often reprice sector leaders over 1-4 weeks.",
            risk_factors="Policy reversals, macro shocks, or earnings misses can invalidate the thesis.",
            thesis_conditions="Event confirmation, sector follow-through, no major contradictory policy updates.",
            confidence_score=event.confidence,
        )
        db.add(report)

    db.commit()
    db.refresh(report)
    return report


def filter_assets_for_broker(
    db: Session,
    report_id: int,
    broker_name: str,
    preferred_exchanges: str = "",
) -> list[ReportAsset]:
    assets = db.query(ReportAsset).filter(ReportAsset.report_id == report_id).all()
    allowed = db.query(BrokerInstrument).filter(
        BrokerInstrument.broker_name == broker_name,
        BrokerInstrument.active.is_(True),
    ).all()

    if not allowed:
        return [asset for asset in assets if validate_ticker(asset.ticker)]

    # Build preferred exchange set for priority filtering (REQ-BRK-003)
    preferred_set: set[str] = set()
    if preferred_exchanges:
        preferred_set = {e.strip().upper() for e in preferred_exchanges.split(",") if e.strip()}

    if preferred_set:
        preferred_tickers = {row.ticker.upper() for row in allowed if row.exchange.upper() in preferred_set}
        # Use preferred-exchange tickers if any match; otherwise fall back to all allowed
        allowed_tickers = preferred_tickers if preferred_tickers else {row.ticker.upper() for row in allowed}
    else:
        allowed_tickers = {row.ticker.upper() for row in allowed}

    filtered = [asset for asset in assets if asset.ticker.upper() in allowed_tickers]
    return [asset for asset in filtered if validate_ticker(asset.ticker)]
