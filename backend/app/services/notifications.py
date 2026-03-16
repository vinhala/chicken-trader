from sqlalchemy.orm import Session
from typing import Optional

from app.models.entities import Notification


def create_notification(
    db: Session,
    *,
    user_id: int,
    thesis_id: Optional[int],
    title: str,
    body: str,
    recommended_action: str,
    dedupe_key: str,
) -> Optional[Notification]:
    if db.query(Notification).filter(Notification.dedupe_key == dedupe_key).first():
        return None

    notification = Notification(
        user_id=user_id,
        thesis_id=thesis_id,
        title=title,
        body=body,
        recommended_action=recommended_action,
        dedupe_key=dedupe_key,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
