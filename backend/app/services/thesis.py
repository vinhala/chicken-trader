from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import FollowedThesis, ThesisEvaluation, ThesisState
from app.services.notifications import create_notification


def evaluate_thesis_state(thesis: FollowedThesis) -> tuple[ThesisState, str]:
    age_days = (datetime.utcnow() - thesis.followed_at).days
    if age_days >= 21:
        return ThesisState.SELL, "Opportunity window has likely passed for this event-driven thesis."
    if age_days >= 14:
        return ThesisState.WARNING, "Thesis aging; monitor for contradictory developments."
    if age_days >= 7:
        return ThesisState.HOLD, "Waiting for confirmation while maintaining position discipline."
    return ThesisState.ACTIVE, "Thesis remains active with no clear invalidation signals."


def reevaluate_active_theses(db: Session) -> int:
    theses = db.query(FollowedThesis).filter(FollowedThesis.closed.is_(False)).all()
    count = 0
    for thesis in theses:
        state, explanation = evaluate_thesis_state(thesis)
        db.add(ThesisEvaluation(thesis_id=thesis.id, state=state, explanation=explanation))

        if state == ThesisState.SELL:
            thesis.closed = True
            create_notification(
                db,
                user_id=thesis.user_id,
                thesis_id=thesis.id,
                title="Close Position Suggestion",
                body=explanation,
                recommended_action="Close or reassess positions",
                dedupe_key=f"sell:{thesis.id}",
            )
        count += 1

    db.commit()
    return count
