from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.entities import User, WatchlistItem


router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("")
def list_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    return [{"id": r.id, "ticker": r.ticker, "asset_name": r.asset_name} for r in rows]


@router.post("")
def add_watchlist(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ticker = (payload.get("ticker") or "").upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker required")
    row = WatchlistItem(user_id=current_user.id, ticker=ticker, asset_name=payload.get("asset_name", ""))
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ticker already in watchlist")
    db.refresh(row)
    return {"id": row.id, "ticker": row.ticker}


@router.delete("/{watch_id}")
def remove_watchlist(watch_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    row = db.get(WatchlistItem, watch_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
    return {"ok": True}
