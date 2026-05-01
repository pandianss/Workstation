from __future__ import annotations

import json

import pandas as pd

from src.core.paths import project_path
from src.domain.schemas.user import UserAccess
from src.infrastructure.persistence.json_repo import JsonRepository


class AdminService:
    def __init__(self) -> None:
        self.repo = JsonRepository(
            project_path("data", "users.json"),
            [{"username": "admin", "role": "ADMIN", "dept": "ALL"}],
        )
        from src.infrastructure.persistence.master_repository import MasterRepository
        self.master_repo = MasterRepository()

    def list_users(self) -> list[UserAccess]:
        # Start with explicit users from JSON (Admins, etc.)
        users = [UserAccess.model_validate(self._normalize_user(record)) for record in self.repo.read()]
        
        # Add staff members as default USERS
        staff_records = self.master_repo.get_by_category("STAFF")
        user_ids = {u.username for u in users}
        
        for staff in staff_records:
            if staff.code not in user_ids:
                meta = staff.metadata or {}
                sol = str(meta.get("sol", "ALL"))
                users.append(UserAccess(
                    username=staff.code,
                    role="USER",
                    dept=meta.get("dept", "ALL"),
                    depts=[meta.get("dept", "ALL")],
                    name=staff.name_en,
                    designation=meta.get("designation", "Staff"),
                    grade=meta.get("grade", "N/A"),
                    assigned_branches=[sol] if sol != "ALL" else []
                ))
        return users

    def get_users_frame(self) -> pd.DataFrame:
        users = [user.model_dump() for user in self.list_users()]
        return pd.DataFrame(users)

    def get_user(self, username: str) -> UserAccess | None:
        # 1. Check explicit users (Admins take precedence)
        for user in [UserAccess.model_validate(self._normalize_user(record)) for record in self.repo.read()]:
            if user.username == username:
                return user
        
        # 2. Check Staff Master (By Roll No / Code)
        staff_records = self.master_repo.get_by_category("STAFF")
        for staff in staff_records:
            if staff.code == username:
                meta = staff.metadata or {}
                sol = str(meta.get("sol", "ALL"))
                return UserAccess(
                    username=staff.code,
                    role="USER",
                    dept=meta.get("dept", "ALL"),
                    depts=[meta.get("dept", "ALL")],
                    name=staff.name_en,
                    designation=meta.get("designation", "Staff"),
                    grade=meta.get("grade", "N/A"),
                    assigned_branches=[sol] if sol != "ALL" else []
                )
        return None

    def add_user(self, username: str, role: str, dept: str = "ALL") -> UserAccess:
        users = self.repo.read()
        record = {"username": username, "role": role, "dept": dept, "depts": [dept]}
        users.append(record)
        self.repo.write(users)
        return UserAccess.model_validate(self._normalize_user(record))

    def update_user(self, username: str, **updates) -> bool:
        users = self.repo.read()
        updated = False
        for record in users:
            if record.get("username") == username:
                record.update(updates)
                if "dept" in record and "depts" not in record:
                    record["depts"] = [record["dept"]]
                updated = True
                break
        if updated:
            self.repo.write(users)
        return updated

    def _normalize_user(self, record: dict) -> dict:
        normalized = dict(record)
        normalized.setdefault("dept", (normalized.get("depts") or ["ALL"])[0])
        normalized.setdefault("depts", [normalized["dept"]])
        normalized.setdefault("name", normalized["username"])
        normalized.setdefault("assigned_branches", [])
        normalized.setdefault("designation", "System User")
        normalized.setdefault("grade", "N/A")
        normalized.setdefault("rank", 4)
        return normalized
