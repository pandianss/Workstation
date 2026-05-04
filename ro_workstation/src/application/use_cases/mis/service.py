from __future__ import annotations

import datetime
import shutil

import numpy as np
import pandas as pd
import streamlit as st

from src.core.config.config_loader import get_app_settings
from src.core.paths import project_path
from src.core.utils.financial_year import get_fy_start, get_quarter_start, get_next_month_end
from src.domain.schemas.mis import MISFilter, MISSnapshot
from src.infrastructure.persistence.excel_repo import ExcelRepository
from src.infrastructure.persistence.mis_repository import MISRepository
from src.infrastructure.persistence.budget_repository import BudgetRepository
from src.application.services.milestone_service import MilestoneService
from src.infrastructure.persistence.database import get_db_session


class MISAnalyticsService:
    def __init__(self) -> None:
        self.settings = get_app_settings()
        self.mis_dir = project_path("data", "mis")
        self.archive_dir = self.mis_dir / "archive"
        self.excel_repo = ExcelRepository()
        self.repository = MISRepository()
        self.budget_repo = BudgetRepository()

    def _ingest_new_files(self) -> None:
        self.mis_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        for file_path in self.mis_dir.glob("*.xlsx"):
            if self.repository.is_file_ingested(file_path.name):
                continue
            frame = self.excel_repo.read(file_path)
            if "DATE" in frame.columns:
                frame["DATE"] = pd.to_datetime(
                    frame["DATE"].astype(str).str.split(".").str[0],
                    format="%Y%m%d",
                    errors="coerce",
                )
            self.repository.save_records(frame.to_dict("records"))
            self.repository.mark_file_ingested(file_path.name)
            shutil.move(str(file_path), str(self.archive_dir / file_path.name))

    @st.cache_data(show_spinner=True)
    def load_frame(_self) -> pd.DataFrame:
        """Cached data loading and enrichment."""
        # Note: In production, you'd call self._ingest_new_files() elsewhere (e.g. background task)
        # to keep the UI fast. For now, we'll keep it but ensure load_frame is cached properly.
        frame = _self.repository.load_frame()
        if frame.empty:
            return frame
        frame.columns = [column.upper().replace("_", " ") for column in frame.columns]
        frame["DATE"] = pd.to_datetime(frame["DATE"])
        return _self._enrich_metrics(frame)

    def get_data(self, force_ingest: bool = False) -> pd.DataFrame:
        """Main entry point for UI, handles ingestion before loading."""
        # Only check filesystem if explicitly requested or on first load of the session
        if force_ingest or st.session_state.get("mis_needs_ingest", True):
            if any(self.mis_dir.glob("*.xlsx")):
                self._ingest_new_files()
            st.session_state["mis_needs_ingest"] = False
        return self.load_frame()

    @staticmethod
    def _enrich_metrics(frame: pd.DataFrame) -> pd.DataFrame:
        def safe_sum(df, columns):
            existing = [column for column in columns if column in df.columns]
            return df[existing].fillna(0).sum(axis=1) if existing else 0

        frame["CORE RETAIL"] = safe_sum(frame, ["HOUSING", "VEHICLE", "PERSONAL", "MORTGAGE", "EDUCATION", "LIQUIRENT", "OTHER RETAIL"])
        frame["TOTAL ADVANCES"] = safe_sum(frame, ["CORE AGRI", "GOLD", "MSME", "CORE RETAIL"])
        frame["CASA"] = safe_sum(frame, ["SB", "CD"])
        td = frame["TD"].fillna(0) if "TD" in frame.columns else 0
        bulk = frame["BULK DEP"].fillna(0) if "BULK DEP" in frame.columns else 0
        frame["RET TD"] = td - bulk          # FIXED: was "Ret TD" — must match uppercase convention
        frame["TOTAL DEPOSITS"] = safe_sum(frame, ["SB", "CD", "TD"])
        frame["CD RATIO"] = np.where(frame["TOTAL DEPOSITS"] > 0, frame["TOTAL ADVANCES"] / frame["TOTAL DEPOSITS"] * 100, 0).round(2)
        frame["TOTAL CASH"] = safe_sum(frame, ["CASH ON HAND", "ATM CASH", "BC CASH", "BNA CASH"])
        crl = frame["CRL"].fillna(0) if "CRL" in frame.columns else 0
        frame["CASH VS CRL"] = frame["TOTAL CASH"] - crl
        frame["TOTAL RECOVERY"] = safe_sum(frame, ["REC Q1", "REC Q2", "REC Q3", "REC Q4"])
        npa = frame["NPA"].fillna(0) if "NPA" in frame.columns else 0
        frame["NPA %"] = np.where(frame["TOTAL ADVANCES"] > 0, npa / frame["TOTAL ADVANCES"] * 100, 0).round(2)
        return frame

    def build_snapshot(self, filters: MISFilter) -> MISSnapshot | None:
        frame = self.get_data()
        if frame.empty:
            return None
        dates = sorted(frame["DATE"].dropna().dt.date.unique())
        selected_date = filters.selected_date or dates[-1]
        selected = frame[frame["DATE"].dt.date == selected_date].copy()
        history = frame.copy()
        if filters.sols:
            selected = selected[selected["SOL"].isin(filters.sols)]
            history = history[history["SOL"].isin(filters.sols)]
        elif self.settings.region_code.isdigit():
            aggregate_sol = int(self.settings.region_code)
            regional = selected[selected["SOL"] == aggregate_sol]
            selected = regional if not regional.empty else selected
            history = history[history["SOL"] == aggregate_sol] if not history[history["SOL"] == aggregate_sol].empty else history

        kpis = {
            "Total Advances": float(selected["TOTAL ADVANCES"].sum()) if "TOTAL ADVANCES" in selected.columns else 0.0,
            "Total Deposits": float(selected["TOTAL DEPOSITS"].sum()) if "TOTAL DEPOSITS" in selected.columns else 0.0,
            "NPA": float(selected["NPA"].sum()) if "NPA" in selected.columns else 0.0,
            "CD Ratio": float(selected["CD RATIO"].mean()) if "CD RATIO" in selected.columns else 0.0,
        }
        
        # Milestone Record
        milestones = None
        milestone_breakthroughs = None
        with get_db_session() as session:
            ms = MilestoneService(session)
            milestones = ms.get_all_at_milestones()
            milestone_breakthroughs = ms.get_milestone_achievements()

        sols = sorted(frame["SOL"].dropna().astype(int).unique().tolist())
        return MISSnapshot(
            selected_date=selected_date,
            available_dates=dates,
            available_sols=sols,
            kpis=kpis,
            rows=selected.to_dict("records"),
            history_rows=history.to_dict("records"),
            milestones=milestones,
            milestone_breakthroughs=milestone_breakthroughs
        )

    def get_performance_metrics(self, selected_date: datetime.date, metric_name: str = "TOTAL ADVANCES", sols: list[int] | None = None) -> dict:
        frame = self.get_data()
        if frame.empty:
            return {}

        # Handle casing
        metric_name = metric_name.upper()

        # Filter frame by SOLs if provided, else by region aggregate if available
        filtered_history = frame.copy()
        if sols:
            filtered_history = filtered_history[filtered_history["SOL"].isin(sols)]
        elif self.settings.region_code.isdigit():
            reg_sol = int(self.settings.region_code)
            # Try to filter by regional aggregate SOL first
            regional_data = filtered_history[filtered_history["SOL"] == reg_sol]
            if not regional_data.empty:
                filtered_history = regional_data

        # 1. FY Growth (from April 1st)
        fy_start = get_fy_start(selected_date)
        
        # Get actuals for selected date
        current_data = filtered_history[filtered_history["DATE"].dt.date == selected_date]
        current_val = current_data[metric_name].sum() if not current_data.empty and metric_name in current_data.columns else 0.0

        # Get actuals for FY Start (using same SOL filter)
        fy_start_data = filtered_history[filtered_history["DATE"].dt.date == fy_start]
        if fy_start_data.empty:
            # Fallback: find the earliest record in this FY
            fy_start_data = filtered_history[filtered_history["DATE"].dt.date >= fy_start].sort_values("DATE").head(1)
        
        fy_start_val = fy_start_data[metric_name].sum() if not fy_start_data.empty and metric_name in fy_start_data.columns else 0.0
        
        # If still zero, try any earliest record ever as last resort to avoid 10000% growth
        if fy_start_val == 0:
            fy_start_data = filtered_history.sort_values("DATE").head(1)
            fy_start_val = fy_start_data[metric_name].sum() if not fy_start_data.empty and metric_name in fy_start_data.columns else 0.0

        fy_growth = current_val - fy_start_val
        fy_growth_pct = (fy_growth / fy_start_val * 100) if fy_start_val > 0 else 0.0

        # 2. Gaps to Budget
        curr_month_str = selected_date.strftime("%Y-%m")
        next_month_date = get_next_month_end(selected_date)
        next_month_str = next_month_date.strftime("%Y-%m")

        target_curr_month = self.budget_repo.get_target(metric_name, curr_month_str, sols=sols)
        target_next_month = self.budget_repo.get_target(metric_name, next_month_str, sols=sols)
        target_fy = self.budget_repo.get_target(metric_name, sols=sols)

        return {
            "current_actual": current_val,
            "fy_start_actual": fy_start_val,
            "fy_growth": fy_growth,
            "fy_growth_pct": fy_growth_pct,
            "gap_current_month": target_curr_month - current_val,
            "gap_next_month": target_next_month - current_val,
            "gap_fy": target_fy - current_val,
            "targets": {
                "month": target_curr_month,
                "next_month": target_next_month,
                "fy": target_fy
            }
        }
