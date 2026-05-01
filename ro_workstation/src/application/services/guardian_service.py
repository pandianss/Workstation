from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.core.paths import project_path
from src.domain.schemas.guardian import GuardianFollowUp
from src.infrastructure.persistence.json_repo import JsonRepository


class GuardianService:
    def __init__(self) -> None:
        self.repo = JsonRepository(project_path("data", "guardian_followups.json"), [])

    def record_followup(self, go_username: str, sol: str, details: str) -> GuardianFollowUp:
        records = self.repo.read()
        payload = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "go_username": go_username,
            "sol": sol,
            "details": details,
        }
        records.append(payload)
        self.repo.write(records)
        return GuardianFollowUp.model_validate(payload)

    def list_followups(self, sol: str | None = None, go_username: str | None = None) -> list[GuardianFollowUp]:
        records = [GuardianFollowUp.model_validate(item) for item in self.repo.read()]
        if sol:
            records = [item for item in records if item.sol == sol]
        if go_username:
            records = [item for item in records if item.go_username == go_username]
        return records

    def as_frame(self) -> pd.DataFrame:
        return pd.DataFrame(item.model_dump() for item in self.list_followups())
