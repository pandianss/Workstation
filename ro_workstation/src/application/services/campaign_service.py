from __future__ import annotations

import datetime
from typing import Any
from src.core.paths import project_path
from src.infrastructure.persistence.json_repo import JsonRepository


class CampaignService:
    def __init__(self) -> None:
        self.repo = JsonRepository(
            project_path("data", "campaigns.json"),
            {"campaigns": [
                {
                    "name": "CASA Mahotsav",
                    "start_date": "2026-04-01",
                    "end_date": "2026-06-30",
                    "target_metric": "CASA",
                    "target_value": 5000.0,
                    "status": "Active"
                }
            ]}
        )

    def list_campaigns(self) -> list[dict[str, Any]]:
        return self.repo.read().get("campaigns", [])

    def create_campaign(self, campaign: dict[str, Any]) -> None:
        data = self.repo.read()
        data["campaigns"].append(campaign)
        self.repo.write(data)
