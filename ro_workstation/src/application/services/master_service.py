from __future__ import annotations

import pandas as pd
from src.infrastructure.persistence.master_repository import MasterRepository

class MasterService:
    def __init__(self) -> None:
        self.repo = MasterRepository()

    def get_units_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("UNIT")
        data = []
        for r in records:
            meta = r.metadata or {}
            data.append({
                "Code": str(r.code),
                "Name": r.name_en,
                "Type": meta.get("type"),
                "District": meta.get("district"),
                "Population Group": meta.get("populationGroup"),
                "Head": str(meta.get("headUserId")) if meta.get("headUserId") else "None",
                "2nd Line": str(meta.get("secondLineUserId")) if meta.get("secondLineUserId") else "None",
                "Active": r.is_active
            })
        return pd.DataFrame(data)

    def get_staff_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("STAFF")
        data = []
        for r in records:
            meta = r.metadata or {}
            data.append({
                "Roll No": str(r.code),
                "Name (En)": r.name_en,
                "Name (Hi)": r.name_hi or "",
                "Name (Ta)": r.name_local or "",
                "Designation": meta.get("designation"),
                "Grade": meta.get("grade"),
                "Branch SOL": str(meta.get("sol")) if meta.get("sol") else "",
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

    def update_unit_authorities(self, unit_code: str, head_roll: str, second_line_roll: str) -> bool:
        records = self.repo.get_by_category("UNIT")
        unit = next((r for r in records if r.code == str(unit_code)), None)
        if not unit:
            return False
            
        meta = unit.metadata or {}
        meta["headUserId"] = str(head_roll) if head_roll else None
        meta["secondLineUserId"] = str(second_line_roll) if second_line_roll else None
        unit.metadata = meta
        
        self.repo.save(unit)
        return True

    def update_staff_names(self, roll_no: str, name_hi: str, name_ta: str) -> bool:
        records = self.repo.get_by_category("STAFF")
        staff = next((r for r in records if r.code == str(roll_no)), None)
        if not staff:
            return False
            
        staff.name_hi = name_hi
        staff.name_local = name_ta
        
        self.repo.save(staff)
        return True

    def get_ro_executives(self) -> list[dict]:
        records = self.repo.get_by_category("STAFF")
        execs = []
        for r in records:
            meta = r.metadata or {}
            grade = str(meta.get("grade", "")).upper()
            sol = str(meta.get("sol", ""))
            
            # Regional Office SOL is 3933, Scale IV and above
            is_exec = any(x in grade for x in ["IV", "V", "VI", "VII"])
            if sol == "3933" and is_exec:
                execs.append({
                    "roll": r.code,
                    "name": f"{r.name_en} ({meta.get('designation')})",
                    "full_name": r.name_en,
                    "designation": meta.get("designation"),
                    "grade": meta.get("grade")
                })
        return sorted(execs, key=lambda x: x["name"])
