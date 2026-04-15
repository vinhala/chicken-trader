import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ThesisState(str, enum.Enum):
    ACTIVE = "Active"
    HOLD = "Hold"
    WARNING = "Warning"
    SELL = "Sell"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DisclaimerConsent(Base):
    __tablename__ = "disclaimer_consents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    accepted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    disclaimer_text: Mapped[str] = mapped_column(Text)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headline: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str] = mapped_column(Text)
    market_interpretation: Mapped[str] = mapped_column(Text)
    sector: Mapped[str] = mapped_column(String(120), default="General")
    confidence: Mapped[str] = mapped_column(String(32), default="Medium")
    expected_market_impact: Mapped[str] = mapped_column(String(32), default="Medium")
    relevance_score: Mapped[int] = mapped_column(Integer, default=50, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    dedupe_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InvestmentReport(Base):
    __tablename__ = "investment_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    event_summary: Mapped[str] = mapped_column(Text)
    market_impact: Mapped[str] = mapped_column(Text)
    context: Mapped[str] = mapped_column(Text, default="")
    risk_factors: Mapped[str] = mapped_column(Text, default="")
    thesis_conditions: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[str] = mapped_column(String(32), default="Medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReportAsset(Base):
    __tablename__ = "report_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("investment_reports.id", ondelete="CASCADE"), index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    asset_name: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[str] = mapped_column(String(50), default="stock")
    relationship: Mapped[str] = mapped_column(Text, default="")
    direction: Mapped[str] = mapped_column(String(20), default="up")
    justification: Mapped[str] = mapped_column(Text, default="")



class FollowedThesis(Base):
    __tablename__ = "followed_theses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("investment_reports.id", ondelete="CASCADE"), index=True)
    securities_json: Mapped[str] = mapped_column(Text)
    thesis_summary: Mapped[str] = mapped_column(Text)
    report_headline: Mapped[str] = mapped_column(Text, default="")
    time_horizon: Mapped[str] = mapped_column(String(50), default="event-driven")
    thesis_conditions: Mapped[str] = mapped_column(Text, default="")
    followed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class ThesisEvaluation(Base):
    __tablename__ = "thesis_evaluations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thesis_id: Mapped[int] = mapped_column(ForeignKey("followed_theses.id", ondelete="CASCADE"), index=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    state: Mapped[ThesisState] = mapped_column(Enum(ThesisState), default=ThesisState.ACTIVE)
    explanation: Mapped[str] = mapped_column(Text)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    thesis_id: Mapped[Optional[int]] = mapped_column(ForeignKey("followed_theses.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(String(255), default="Review")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    dedupe_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)


