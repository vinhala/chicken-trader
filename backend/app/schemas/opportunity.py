from datetime import datetime

from pydantic import BaseModel


class AssetOut(BaseModel):
    ticker: str
    asset_name: str
    asset_type: str
    relationship: str
    direction: str
    justification: str


class OpportunityListItem(BaseModel):
    event_id: int
    headline: str
    summary: str
    sector: str
    confidence: str
    expected_market_impact: str
    created_at: datetime


class OpportunityDetail(BaseModel):
    event_id: int
    headline: str
    event_summary: str
    market_impact: str
    context: str
    risk_factors: str
    confidence_score: str
    thesis_conditions: str
    assets: list[AssetOut]
    assets_warning: str | None = None
    created_at: datetime


class FollowRequest(BaseModel):
    time_horizon: str = "event-driven"
