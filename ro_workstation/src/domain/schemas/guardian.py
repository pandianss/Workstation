from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class GuardianFollowUp(BaseModel):
    timestamp: datetime
    date: str
    go_username: str
    sol: str
    details: str
