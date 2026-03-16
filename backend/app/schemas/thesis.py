from datetime import datetime
from pydantic import BaseModel


class ThesisOut(BaseModel):
    id: int
    event_id: int
    thesis_summary: str
    time_horizon: str
    followed_at: datetime
    closed: bool
    latest_state: str
    latest_explanation: str
