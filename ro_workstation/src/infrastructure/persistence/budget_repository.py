from __future__ import annotations

import json
from typing import Any

from src.core.paths import project_path
from src.infrastructure.persistence.json_repo import JsonRepository


class BudgetRepository:
    def __init__(self) -> None:
        self.repo = JsonRepository(
            project_path("data", "budgets.json"),
            {
                "defaults": {
                    "Total Advances": 500000.0,  # Mock values in Lacs
                    "Total Deposits": 600000.0,
                    "CASA": 200000.0,
                    "NPA": 15000.0
                },
                "monthly_targets": {} # keyed by YYYY-MM
            }
        )

    def get_target(self, metric: str, year_month: str | None = None) -> float:
        data = self.repo.read()
        if year_month and year_month in data.get("monthly_targets", {}):
            return data["monthly_targets"][year_month].get(metric, data["defaults"].get(metric, 0.0))
        return data["defaults"].get(metric, 0.0)

    def save_target(self, metric: str, value: float, year_month: str | None = None) -> None:
        data = self.repo.read()
        if year_month:
            if "monthly_targets" not in data: data["monthly_targets"] = {}
            if year_month not in data["monthly_targets"]: data["monthly_targets"][year_month] = {}
            data["monthly_targets"][year_month][metric] = value
        else:
            data["defaults"][metric] = value
        self.repo.write(data)
