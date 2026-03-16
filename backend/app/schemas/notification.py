from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    recommended_action: str
    read: bool
    created_at: datetime
