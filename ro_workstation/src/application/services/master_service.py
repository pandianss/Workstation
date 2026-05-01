from __future__ import annotations

import pandas as pd
from src.infrastructure.persistence.master_repository import MasterRepository

class MasterService:
    def __init__(self) -> None:
        self.repo = MasterRepository()

    def get_branches_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("BRANCH")
        data = []
        for r in records:
            meta = r.metadata or {}
            data.append({
                "Code": r.code,
                "Name": r.name_en,
                "Type": meta.get("type"),
                "District": meta.get("district"),
                "Population Group": meta.get("populationGroup"),
                "Pincode": meta.get("pincode"),
                "Active": r.is_active
            })
        return pd.DataFrame(data)

    def get_staff_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("STAFF")
        data = []
        for r in records:
            meta = r.metadata or {}
            data.append({
                "Roll No": r.code,
                "Name": r.name_en,
                "Designation": meta.get("designation"),
                "Grade": meta.get("grade"),
                "Branch SOL": meta.get("sol"),
                "Active": r.is_active
            })
        return pd.DataFrame(data)

    def get_departments_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("DEPARTMENT")
        data = []
        for r in records:
            data.append({
                "Code": r.code,
                "Name": r.name_en,
                "Active": r.is_active
            })
        return pd.DataFrame(data)
