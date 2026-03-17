import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.entities import Article, FollowedThesis, ThesisEvaluation, ThesisState
from app.services.notifications import create_notification

logger = logging.getLogger(__name__)

_REEVALUATE_PROMPT = """You are a financial analyst evaluating an active investment thesis.

Original thesis: {thesis_summary}
Thesis conditions: {thesis_conditions}
Time horizon: {time_horizon}
Days since initiated: {age_days}
Securities involved: {securities}

Recent news developments:
{news_context}
{market_context}
Based on this information, assess whether the thesis is still valid.

Return a JSON object:
{{
  "status": "Active or Warning or Close Suggested",
  "rationale": "2-3 sentence explanation of your assessment",
  "affected_securities": ["list of ticker symbols most relevant to this update"],
  "suggested_action": "specific, actionable recommendation for the user"
}}

Active = thesis conditions remain intact, no significant contradictory developments.
Warning = new information partially challenges the thesis; user should review.
Close Suggested = thesis has played out, been invalidated, or the opportunity window has likely passed.

Return valid JSON only."""


def _call_openai_reevaluate(prompt: str) -> Optional[dict]:
    from app.core.config import settings
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as exc:
        logger.warning("OpenAI reevaluation failed: %s", exc)
        return None


def _time_based_state(age_days: int) -> ThesisState:
    if age_days >= 21:
        return ThesisState.SELL
    if age_days >= 14:
        return ThesisState.WARNING
    if age_days >= 7:
        return ThesisState.HOLD
    return ThesisState.ACTIVE


def evaluate_thesis(db: Session, thesis: FollowedThesis) -> tuple[ThesisState, str, list[str], str]:
    """Evaluate a single thesis using AI + market context.

    Returns (state, rationale, affected_securities, suggested_action).
    """
    age_days = (datetime.utcnow() - thesis.followed_at).days

    # Fetch recent articles for the event as monitoring context (REQ-MON-002)
    recent_articles = (
        db.query(Article)
        .filter(Article.event_id == thesis.event_id)
        .order_by(Article.published_at.desc())
        .limit(10)
        .all()
    )
    news_context = "\n".join(
        f"- {a.title} ({a.source}, {a.published_at.strftime('%Y-%m-%d')})"
        for a in recent_articles
    ) or "No recent news articles found for this event."

    # Parse securities and fetch current market prices (REQ-MON-002)
    securities: list[str] = []
    try:
        securities = json.loads(thesis.securities_json) if thesis.securities_json else []
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse securities_json for thesis %d: %s", thesis.id, exc)

    from app.services.market import get_price_snapshot
    price_data = get_price_snapshot(securities)
    market_context = ""
    if price_data:
        market_context = "\nCurrent market prices:\n" + "\n".join(
            f"- {ticker}: ${price:.2f}" for ticker, price in price_data.items()
        )

    prompt = _REEVALUATE_PROMPT.format(
        thesis_summary=thesis.thesis_summary or "Not specified",
        thesis_conditions=thesis.thesis_conditions or "Not specified",
        time_horizon=thesis.time_horizon or "Event-driven",
        age_days=age_days,
        securities=", ".join(securities) if securities else "None specified",
        news_context=news_context,
        market_context=market_context,
    )

    ai_result = _call_openai_reevaluate(prompt)

    if ai_result:
        ai_status = ai_result.get("status", "")
        _status_map = {
            "Active": ThesisState.ACTIVE,
            "Warning": ThesisState.WARNING,
            "Close Suggested": ThesisState.SELL,
        }
        if ai_status not in _status_map:
            logger.warning("AI returned unrecognized status %r for thesis %d, falling back to time-based", ai_status, thesis.id)
        state = _status_map.get(ai_status) or _time_based_state(age_days)
        rationale = ai_result.get("rationale") or "AI evaluation completed."
        affected = ai_result.get("affected_securities") or securities
        action = ai_result.get("suggested_action") or "Review your position."
    else:
        # Fallback to time-based evaluation when AI is unavailable
        state = _time_based_state(age_days)
        rationale = {
            ThesisState.SELL: "Opportunity window has likely passed for this event-driven thesis.",
            ThesisState.WARNING: "Thesis aging; monitor for contradictory developments.",
            ThesisState.HOLD: "Waiting for confirmation while maintaining position discipline.",
            ThesisState.ACTIVE: "Thesis remains active with no clear invalidation signals.",
        }[state]
        affected = securities
        action = "Review your position." if state in (ThesisState.WARNING, ThesisState.SELL) else "Continue monitoring."

    return state, rationale, affected, action


def reevaluate_active_theses(db: Session) -> int:
    theses = db.query(FollowedThesis).filter(FollowedThesis.closed.is_(False)).all()
    count = 0
    for thesis in theses:
        state, explanation, affected_securities, suggested_action = evaluate_thesis(db, thesis)
        db.add(ThesisEvaluation(thesis_id=thesis.id, state=state, explanation=explanation))

        if state == ThesisState.SELL:
            thesis.closed = True
            create_notification(
                db,
                user_id=thesis.user_id,
                thesis_id=thesis.id,
                title="Close Position Suggested",
                body=explanation,
                recommended_action=suggested_action,
                dedupe_key=f"sell:{thesis.id}:{datetime.utcnow().date()}",
            )
        elif state == ThesisState.WARNING:
            create_notification(
                db,
                user_id=thesis.user_id,
                thesis_id=thesis.id,
                title="Thesis Warning",
                body=explanation,
                recommended_action=suggested_action,
                dedupe_key=f"warning:{thesis.id}:{datetime.utcnow().date()}",
            )
        count += 1

    db.commit()
    return count
