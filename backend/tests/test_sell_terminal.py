from datetime import datetime, timedelta

from app.models.entities import Event, FollowedThesis, InvestmentReport, Notification, ThesisEvaluation, User
from app.services.thesis import reevaluate_active_theses


def test_sell_is_terminal_and_not_duplicated(db_session):
    user = User(email="sell@test.com", password_hash="x")
    db_session.add(user)
    db_session.flush()

    event = Event(headline="Old event", summary="s", market_interpretation="m", sector="Macro", confidence="High")
    db_session.add(event)
    db_session.flush()

    report = InvestmentReport(
        event_id=event.id,
        event_summary="e",
        market_impact="m",
        context="c",
        risk_factors="r",
        thesis_conditions="t",
        confidence_score="High",
    )
    db_session.add(report)
    db_session.flush()

    thesis = FollowedThesis(
        user_id=user.id,
        event_id=event.id,
        report_id=report.id,
        securities_json='["SPY"]',
        thesis_summary="summary",
        time_horizon="event-driven",
        thesis_conditions="cond",
        followed_at=datetime.utcnow() - timedelta(days=30),
        closed=False,
    )
    db_session.add(thesis)
    db_session.commit()

    reevaluate_active_theses(db_session)
    reevaluate_active_theses(db_session)

    notifications = db_session.query(Notification).filter(Notification.user_id == user.id).all()
    evaluations = db_session.query(ThesisEvaluation).filter(ThesisEvaluation.thesis_id == thesis.id).all()
    refreshed = db_session.get(FollowedThesis, thesis.id)

    assert refreshed.closed is True
    assert len(notifications) == 1
    assert len(evaluations) == 1
