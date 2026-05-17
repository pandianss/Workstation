from __future__ import annotations
import datetime
import os
import json
import logging
import pandas as pd
import streamlit as st
from src.core.paths import project_path
from src.core.config.config_loader import get_app_settings
from src.application.services.translation_service import SalutationMapper, DesignationMapper
from src.application.services.master_sync_service import MasterSyncService
from src.application.services.master_data_service import MasterDataService
from src.infrastructure.persistence.master_repository import MasterRepository
from src.domain.models.master import MasterRecord

logger = logging.getLogger(__name__)

class MasterService:
    def __init__(self, repo: MasterRepository | None = None) -> None:
        self.repo = repo or MasterRepository()
        self.sync_service = MasterSyncService(self.repo)
        self.data_service = MasterDataService(self.repo)
        self.settings = get_app_settings()

    @st.cache_resource(show_spinner=False, ttl=3600)
    def get_by_category(_self, category: str) -> list[MasterRecord]:
        """Returns all records for a given category (STAFF, UNIT, DEPT). Cached for speed."""
        return _self.repo.get_by_category(category)

    # Delegated Data Methods
    @st.cache_data(show_spinner=False, ttl=3600)
    def get_units_frame(_self) -> pd.DataFrame:
        return _self.data_service.get_units_frame()

    @st.cache_data(show_spinner=False, ttl=3600)
    def get_departments_frame(_self) -> pd.DataFrame:
        return _self.data_service.get_departments_frame()

    @st.cache_data(show_spinner=False, ttl=3600)
    def get_staff_frame(_self) -> pd.DataFrame:
        return _self.data_service.get_staff_frame()

    # Delegated Sync Methods
    def sync_staff_from_csv(self) -> None:
        self.sync_service.sync_staff_from_csv()
        self._update_sync_state()

    def sync_units_from_csv(self) -> None:
        self.sync_service.sync_units_from_csv()

    def sync_departments_from_csv(self) -> None:
        self.sync_service.sync_departments_from_csv()

    def update_master_file(self, category: str, file_bytes: bytes, filename: str) -> bool:
        """Saves uploaded file to the appropriate location and triggers sync."""
        target_map = {
            "STAFF": project_path("files", "Staff.csv"),
            "UNIT": project_path("files", "branches.csv"),
            "DEPT": project_path("files", "departments.csv"),
            "BUDGET": project_path("files", "Budget3.csv")
        }
        
        target_path = target_map.get(category.upper())
        if not target_path: return False
        
        # Backup existing
        if target_path.exists():
            backup_path = target_path.with_suffix(f".bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.rename(target_path, backup_path)
            
        with open(target_path, "wb") as f:
            f.write(file_bytes)
            
        # Trigger appropriate sync
        if category.upper() == "STAFF": self.sync_staff_from_csv()
        elif category.upper() == "UNIT": self.sync_units_from_csv()
        elif category.upper() == "DEPT": self.sync_departments_from_csv()
        
        self._update_sync_state()
        return True

    def sync_if_needed(self, force: bool = False) -> None:
        state_path = project_path("data", "master_sync.json")
        state = {}
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Ignoring unreadable master sync state %s: %s", state_path, exc)
                state = {}
        
        files = {
            "staff_csv": project_path("files", "Staff.csv"),
            "branches": project_path("files", "branches.csv"),
            "departments": project_path("files", "departments.csv")
        }
        
        needs_sync = force or not state_path.exists()
        for key, path in files.items():
            if not path.exists(): continue
            mtime = os.path.getmtime(path)
            if state.get(key) != mtime:
                needs_sync = True
                state[key] = mtime
        
        if needs_sync:
            logger.info("Syncing master data...")
            self.sync_units_from_csv()
            self.sync_staff_from_csv()
            self.sync_departments_from_csv()
            self._update_sync_state(state, files)

    def _update_sync_state(self, state: dict | None = None, files: dict | None = None) -> None:
        state_path = project_path("data", "master_sync.json")
        if state is None:
            state = {"last_sync": str(datetime.datetime.now())}
        else:
            state["last_sync"] = str(datetime.datetime.now())
            if files:
                for key, path in files.items():
                    if path.exists(): state[key] = os.path.getmtime(path)
        
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        
        # Invalidate Streamlit cache if in Streamlit context
        try:
            import streamlit as st
            st.cache_data.clear()
        except Exception as exc:
            logger.debug("Streamlit cache clear skipped: %s", exc)

    # Staff Management Logic
    @st.cache_data(show_spinner=False, ttl=3600)
    def get_ro_executives(_self) -> list[dict[str, str]]:
        staff = _self.get_by_category("STAFF")
        execs = []
        region_code = _self.settings.region_code
        for s in staff:
            meta = s.metadata or {}
            if str(meta.get("sol")) == region_code:
                grade = meta.get("grade", "")
                desig = meta.get("designation", "").upper()
                
                # Check explicit grade first
                is_exec = any(g in grade for g in ["MM II", "MM III", "SM IV", "SM V", "TEG VI", "TEG VII"])
                
                # Fallback to designation keywords if grade is missing
                if not grade or grade.strip() == "":
                    if any(kw in desig for kw in ["MANAGER", "CHIEF", "REGIONAL", "AGM", "DGM", "GM"]):
                        if "ASST" not in desig and "ASSISTANT" not in desig:
                            is_exec = True
                
                if is_exec:
                    execs.append({"roll": s.code, "name": s.name_en})
        return sorted(execs, key=lambda x: x["name"])

    def allot_staff_to_departments(self, roll: str, dept_codes: list[str]) -> bool:
        staff = next((r for r in self.repo.get_by_category("STAFF") if r.code == roll), None)
        if not staff: return False
        meta = staff.metadata or {}
        meta["departments"] = dept_codes
        staff.metadata = meta
        self.repo.save(staff)
        return True

    def update_staff_details(self, roll: str, name_hi: str, name_ta: str, sol: str, desig: str, gender: str, p_from: str, p_to: str) -> bool:
        staff_list = self.repo.get_by_category("STAFF")
        staff = next((s for s in staff_list if s.code == roll), None)
        if not staff: return False
        
        staff.name_hi = name_hi
        staff.name_local = name_ta
        meta = staff.metadata or {}
        
        if meta.get("sol") != sol or meta.get("designation") != desig:
            history = meta.get("postings", [])
            history.append({
                "sol": meta.get("sol"),
                "designation": meta.get("designation"),
                "from": meta.get("posting_from"),
                "to": datetime.date.today().strftime("%d.%m.%Y")
            })
            meta["postings"] = history
            
        tr_desig = DesignationMapper.get_trilingual(desig)
        meta.update({
            "sol": sol, "designation": desig,
            "desig_en": tr_desig["en"], "desig_hi": tr_desig["hi"], "desig_ta": tr_desig["ta"],
            "posting_from": p_from, "posting_to": p_to, "gender": gender
        })
        staff.metadata = meta
        self.repo.save(staff)
        
        try:
            self._write_back_to_staff_csv()
        except Exception as e:
            logger.warning(f"Failed to update Staff.csv: {e}")
        return True

    def _write_back_to_staff_csv(self) -> None:
        csv_path = project_path("files", "Staff.csv")
        df = self.get_staff_frame()
        # Staged write to prevent data loss
        temp_path = csv_path.with_suffix(".tmp")
        df.to_csv(temp_path, index=False)
        if csv_path.exists():
            os.replace(temp_path, csv_path)
        else:
            os.rename(temp_path, csv_path)

    def get_branch_manager(self, sol: str) -> dict:
        staff = self.repo.get_by_category("STAFF")
        units = self.repo.get_by_category("UNIT")
        target_sol = str(sol).zfill(4)
        
        manager = None
        unit = next((u for u in units if str(u.code).zfill(4) == target_sol), None)
        if unit:
            u_meta = unit.metadata or {}
            head_roll = u_meta.get("headUserId")
            if head_roll:
                manager = next((s for s in staff if str(s.code) == str(head_roll)), None)

        if not manager:
            for s in staff:
                meta = s.metadata or {}
                if str(meta.get("sol")).zfill(4) == target_sol and meta.get("status") == "BH":
                    manager = s
                    break
        
        if manager:
            meta = manager.metadata or {}
            sal = SalutationMapper.get_trilingual(meta.get("gender", "M"))
            tr_desig = DesignationMapper.get_trilingual(meta.get("designation", "Branch Manager"))
            return {
                "name": manager.name_en, "name_hi": manager.name_hi or manager.name_en, "name_ta": manager.name_local or manager.name_en,
                "sal_en": sal["en"], "sal_hi": sal["hi"], "sal_ta": sal["ta"],
                "designation": tr_desig["en"], "desig_en": tr_desig["en"], "desig_hi": tr_desig["hi"], "desig_ta": tr_desig["ta"],
                "grade": meta.get("grade"), "roll": manager.code
            }
        
        return {
            "name": "The Branch Manager", "name_hi": "शाखा प्रबंधक", "name_ta": "கிளை மேலாளர்",
            "sal_en": "The", "sal_hi": "माननीय", "sal_ta": "மதிப்பிற்குரிய",
            "designation": "Branch Manager", "desig_en": "Branch Manager", "desig_hi": "शाखा प्रबंधक", "desig_ta": "கிளை மேலாளர்",
            "grade": "N/A", "roll": "00000"
        }
