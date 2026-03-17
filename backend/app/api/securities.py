from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.entities import User
from app.services.market import get_security_detail


router = APIRouter(prefix="/securities", tags=["securities"])


@router.get("/{ticker}")
def security_detail(ticker: str, current_user: User = Depends(get_current_user)) -> dict:
    detail = get_security_detail(ticker)
    if detail is None:
        raise HTTPException(status_code=404, detail="Security not found")
    return detail
