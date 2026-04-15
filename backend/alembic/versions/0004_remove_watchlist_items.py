"""remove watchlist_items table

Revision ID: 0004_remove_watchlist_items
Revises: 0003_add_expected_market_impact
Create Date: 2026-04-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_remove_watchlist_items"
down_revision = "0003_add_expected_market_impact"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("watchlist_items")


def downgrade() -> None:
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("asset_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "ticker", name="uq_user_watchlist_ticker"),
    )
    op.create_index(op.f("ix_watchlist_items_ticker"), "watchlist_items", ["ticker"], unique=False)
    op.create_index(op.f("ix_watchlist_items_user_id"), "watchlist_items", ["user_id"], unique=False)
