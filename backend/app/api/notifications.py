from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.entities import Notification, User
from app.schemas.notification import NotificationOut


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[NotificationOut]:
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        NotificationOut(
            id=r.id,
            title=r.title,
            body=r.body,
            recommended_action=r.recommended_action,
            read=r.read,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    row = db.get(Notification, notification_id)
    if row and row.user_id == current_user.id:
        row.read = True
        db.commit()
    return {"ok": True}
