import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.entities import Event, FollowedThesis, ReportAsset, User
from app.schemas.opportunity import AssetOut, FollowRequest, OpportunityDetail, OpportunityListItem
from app.services.ai import generate_report_for_event


router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityListItem])
def list_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OpportunityListItem]:
    from datetime import datetime, timedelta

    _ = current_user
    # Calculate the start of yesteday
    start_of_yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    impact_order = case(
        (Event.expected_market_impact == "High", 1),
        (Event.expected_market_impact == "Medium", 2),
        else_=3,
    )
    events = (
        db.query(Event)
        .filter(Event.created_at >= start_of_yesterday)
        .order_by(impact_order, Event.relevance_score.desc(), Event.created_at.desc())
        .limit(25)
        .all()
    )
    return [
        OpportunityListItem(
            event_id=e.id,
            headline=e.headline,
            summary=e.summary,
            sector=e.sector,
            confidence=e.confidence,
            expected_market_impact=e.expected_market_impact,
        )
        for e in events
    ]


@router.get("/{event_id}", response_model=OpportunityDetail)
def opportunity_detail(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OpportunityDetail:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    report = generate_report_for_event(db, event)
    assets = db.query(ReportAsset).filter(ReportAsset.report_id == report.id).all()
    assets_warning = "No assets could be determined for this opportunity at the moment." if not assets else None
    return OpportunityDetail(
        event_id=event.id,
        headline=event.headline,
        event_summary=report.event_summary,
        market_impact=report.market_impact,
        context=report.context,
        risk_factors=report.risk_factors,
        confidence_score=report.confidence_score,
        thesis_conditions=report.thesis_conditions,
        assets=[
            AssetOut(
                ticker=a.ticker,
                asset_name=a.asset_name,
                asset_type=a.asset_type,
                relationship=a.relationship,
                direction=a.direction,
                justification=a.justification,
            )
            for a in assets
        ],
        assets_warning=assets_warning,
    )


@router.post("/{event_id}/follow")
def follow_opportunity(
    event_id: int,
    payload: FollowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing = (
        db.query(FollowedThesis)
        .filter(FollowedThesis.user_id == current_user.id, FollowedThesis.event_id == event_id)
        .first()
    )
    if existing:
        return {"thesis_id": existing.id, "status": "already_followed"}

    report = generate_report_for_event(db, event)
    assets = db.query(ReportAsset).filter(ReportAsset.report_id == report.id).all()

    thesis = FollowedThesis(
        user_id=current_user.id,
        event_id=event.id,
        report_id=report.id,
        securities_json=json.dumps([a.ticker for a in assets]),
        thesis_summary=report.market_impact,
        report_headline=event.headline,
        time_horizon=payload.time_horizon,
        thesis_conditions=report.thesis_conditions,
    )
    db.add(thesis)
    db.commit()
    db.refresh(thesis)
    return {"thesis_id": thesis.id, "status": "followed"}
