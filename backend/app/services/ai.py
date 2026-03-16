from sqlalchemy.orm import Session

from app.models.entities import BrokerInstrument, Event, InvestmentReport, ReportAsset
from app.services.market import validate_ticker

def generate_report_for_event(db: Session, event: Event) -> InvestmentReport:
    existing = db.query(InvestmentReport).filter(InvestmentReport.event_id == event.id).first()
    if existing:
        return existing

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


def filter_assets_for_broker(db: Session, report_id: int, broker_name: str) -> list[ReportAsset]:
    assets = db.query(ReportAsset).filter(ReportAsset.report_id == report_id).all()
    allowed = db.query(BrokerInstrument).filter(
        BrokerInstrument.broker_name == broker_name,
        BrokerInstrument.active.is_(True),
    ).all()
    if not allowed:
        return [asset for asset in assets if validate_ticker(asset.ticker)]

    allowed_tickers = {row.ticker.upper() for row in allowed}
    filtered = [asset for asset in assets if asset.ticker.upper() in allowed_tickers]
    return [asset for asset in filtered if validate_ticker(asset.ticker)]
