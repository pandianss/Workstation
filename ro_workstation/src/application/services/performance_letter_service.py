from __future__ import annotations
import datetime
from typing import Dict, List, Any
import pandas as pd
from src.infrastructure.persistence.budget_repository import BudgetRepository
from src.infrastructure.persistence.advances_repository import AdvancesRepository
from src.application.use_cases.mis.service import MISAnalyticsService
from src.application.services.document_service import DocumentService
from src.core.utils.financial_year import get_fy_start

class PerformanceLetterService:
    """Service to generate appreciation and explanation letters based on budget performance."""

    # PARAM_GROUPS defines which MIS columns (ALL UPPERCASE) belong to each letter group.
    # Each group generates one appreciation letter (if ≥100% of budget) and one explanation
    # letter (if <90% of budget) per branch.
    #
    # CASA and TD are separate groups per management preference.
    # Subsets are included so the letter table shows the breakdown.
    # SHG is Core Agri (not MSME). Mudra is the only MSME subset tracked here.
    PARAM_GROUPS = {
        "CASA": {
            # Parent: CASA (SB+CD derived). Subsets: SB, CD shown in letter table.
            "parent": "CASA",
            "subsets": ["SB", "CD"],
        },
        "TD": {
            # Parent: TD (Term Deposit). Subset: RET TD (TD minus Bulk Deposits).
            # Total Deposits (CASA+TD) is NOT tracked here — separate budget code needed.
            "parent": "TD",
            "subsets": ["RET TD"],
        },
        "Core Ret": {
            # All Core Retail sub-products. Parent is CORE RETAIL (derived sum).
            "parent": "CORE RETAIL",
            "subsets": ["HOUSING", "VEHICLE", "PERSONAL", "EDUCATION", "MORTGAGE", "LIQUIRENT", "OTHER RETAIL"],
        },
        "MSME": {
            # MSME total. Mudra is a subset (shown in table). SHG is NOT MSME — it is Core Agri.
            "parent": "MSME",
            "subsets": ["MUDRA"],
        },
        "Core Agri": {
            # Core Agri total. Subsets: KCC, SHG, Govt Sponsored Schemes, Other Schematic.
            "parent": "CORE AGRI",
            "subsets": ["KCC", "SHG", "GOVT SPON", "OTH SCHEMATIC"],
        },
        "Jewel Loan": {
            "parent": "GOLD",
            "subsets": ["AGRI JL", "RETAIL JL"],
        },
    }

    # Params for NIL sanction letters. These are checked against the advances portfolio
    # (advances_records table). If a branch has zero accounts opened in the period for
    # the relevant L2_SECTOR, an explanation letter for NIL sanction is generated.
    NIL_SANCTION_PARAMS = {
        "Housing": "Housing",       # advances L2_SECTOR value → display name
        "Vehicle": "Vehicle",
    }

    def __init__(self):
        self.analytics_service = MISAnalyticsService()
        self.budget_repo = BudgetRepository()
        self.advances_repo = AdvancesRepository()
        self.doc_service = DocumentService()

    def _get_actual(self, row: pd.Series, col: str) -> float:
        """Look up a column value from an MIS row. All enriched columns are now uppercase."""
        val = row.get(col.upper(), 0.0)
        return float(val) if pd.notna(val) else 0.0

    def _get_target(self, param: str, year_month: str, sol: int) -> float:
        """Retrieve budget target for a single param and branch."""
        return self.budget_repo.get_target(param, year_month, sols=[sol])

    def get_branch_performance(self, selected_date: datetime.date) -> List[Dict[str, Any]]:
        """Analyses all branches for budget achievement or decline, group by group."""
        df = self.analytics_service.get_data()
        if df.empty:
            return []

        current_month_df = df[df["DATE"].dt.date == selected_date]
        if current_month_df.empty:
            return []

        # Determine FY start (Previous March 31st)
        fy_start_date = get_fy_start(selected_date)
        prev_ye_date = fy_start_date - datetime.timedelta(days=1)
        prev_ye_df = df[df["DATE"].dt.date == prev_ye_date]

        ym = selected_date.strftime("%Y-%m")
        results = []

        for _, row in current_month_df.iterrows():
            sol = int(row["SOL"])
            if sol == 3933:
                continue  # Skip RO aggregate row

            # Get historical data for this branch
            branch_prev_ye = prev_ye_df[prev_ye_df["SOL"] == sol]
            prev_ye_row = branch_prev_ye.iloc[0] if not branch_prev_ye.empty else None

            branch_result = {
                "sol": sol,
                "branch_name": row.get("BRANCH", f"SOL {sol}"),
                "date": selected_date,
                "prev_ye_date": prev_ye_date,
                "groups": {},
            }

            for group_name, cfg in self.PARAM_GROUPS.items():
                parent_col = cfg["parent"]
                all_params = [parent_col] + cfg["subsets"]
                
                # First, gather all stats for this group
                group_stats = []
                has_achievement = False
                has_decline = False

                for param in all_params:
                    actual = self._get_actual(row, param)
                    target = self._get_target(param, ym, sol)
                    fy_start_actual = self._get_actual(prev_ye_row, param) if prev_ye_row is not None else 0
                    fy_growth = actual - fy_start_actual

                    # Calculate percentage, handle division by zero
                    if target > 0:
                        pct = (actual / target * 100)
                    else:
                        pct = 0.0

                    entry = {
                        "parameter": param,
                        "actual": actual,
                        "target": target,
                        "variance": actual - target,
                        "pct": pct,
                        "fy_start_actual": fy_start_actual,
                        "fy_growth": fy_growth,
                        "is_parent": (param == parent_col),
                    }
                    group_stats.append(entry)
                    
                    # Trigger logic
                    if pct >= 100 and target > 0:
                        has_achievement = True
                    
                    # Trigger decline if budget shortfall (<90%) OR negative FY growth
                    if (pct < 90 and target > 0) or (fy_growth < 0):
                        has_decline = True
                    
                    if target <= 0 and actual > 0:
                        has_achievement = True

                # If the group has any achievement, include the FULL breakdown in appreciation
                # If the group has any decline, include the FULL breakdown in explanation
                branch_result["groups"][group_name] = {
                    "achievements": group_stats if has_achievement else [],
                    "declines": group_stats if has_decline else [],
                }

            results.append(branch_result)

        return results

    def get_nil_sanction_branches(
        self, selected_date: datetime.date, advances_report_dt: datetime.date
    ) -> List[Dict[str, Any]]:
        """
        Detects branches with NIL sanctions (zero new accounts opened) under Housing and
        Vehicle during the calendar month of selected_date.

        Uses the advances_records table (sourced from the advances portfolio upload).
        An account is counted as a fresh sanction if open_dt falls within the month.

        Args:
            selected_date: The MIS performance date (used to determine the month window).
            advances_report_dt: The report date to query from advances_records.

        Returns:
            List of dicts with sol, branch_name, and nil_params (list of product names).
        """
        month_start = selected_date.replace(day=1)
        if selected_date.month == 12:
            month_end = selected_date.replace(year=selected_date.year + 1, month=1, day=1)
        else:
            month_end = selected_date.replace(month=selected_date.month + 1, day=1)

        adv_df = self.advances_repo.get_records_by_date(advances_report_dt)
        if adv_df.empty:
            return []

        # Filter to accounts opened within the month
        adv_df["open_dt"] = pd.to_datetime(adv_df["open_dt"]).dt.date
        month_sanctions = adv_df[
            (adv_df["open_dt"] >= month_start) & (adv_df["open_dt"] < month_end)
        ]

        # Get all known branches from MIS
        mis_df = self.analytics_service.get_data()
        mis_row = mis_df[mis_df["DATE"].dt.date == selected_date]
        all_sols = [int(s) for s in mis_row["SOL"].unique() if int(s) != 3933]

        results = []
        for sol in all_sols:
            nil_params = []
            for l2_sector, display_name in self.NIL_SANCTION_PARAMS.items():
                branch_month_sanctions = month_sanctions[
                    (month_sanctions["branch_code"] == sol) &
                    (month_sanctions["l2_sector"] == l2_sector)
                ]
                if len(branch_month_sanctions) == 0:
                    nil_params.append(display_name)

            if nil_params:
                branch_name_rows = mis_row[mis_row["SOL"] == sol]
                branch_name = branch_name_rows["BRANCH"].iloc[0] if not branch_name_rows.empty else f"SOL {sol}"
                results.append({
                    "sol": sol,
                    "branch_name": branch_name,
                    "date": selected_date,
                    "nil_params": nil_params,
                })

        return results

    def generate_letters_zip(
        self,
        performance_data: List[Dict[str, Any]],
        nil_sanction_data: List[Dict[str, Any]] | None = None,
    ) -> bytes:
        """Generates a zip of PDFs for appreciation and explanation letters."""
        import io
        import zipfile

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:

            # --- Performance letters (achievement / shortfall) ---
            for branch in performance_data:
                for group_name, data in branch["groups"].items():

                    if data["achievements"]:
                        payload = {
                            "branch_name": branch["branch_name"],
                            "sol": branch["sol"],
                            "date": branch["date"],
                            "group_name": group_name,
                            "achievements": data["achievements"],
                        }
                        pdf = self.doc_service.generate_performance_appreciation(payload)
                        folder = f"Appreciation_Letters/{group_name.replace(' ', '_')}"
                        zf.writestr(
                            f"{folder}/Appr_{branch['sol']}_{group_name.replace(' ', '_')}.pdf",
                            pdf,
                        )

                    if data["declines"]:
                        payload = {
                            "branch_name": branch["branch_name"],
                            "sol": branch["sol"],
                            "date": branch["date"],
                            "group_name": group_name,
                            "declines": data["declines"],
                        }
                        pdf = self.doc_service.generate_explanation_letter(payload)
                        folder = f"Explanation_Letters/{group_name.replace(' ', '_')}"
                        zf.writestr(
                            f"{folder}/Expl_{branch['sol']}_{group_name.replace(' ', '_')}.pdf",
                            pdf,
                        )

            # --- NIL Sanction letters ---
            if nil_sanction_data:
                for branch in nil_sanction_data:
                    payload = {
                        "branch_name": branch["branch_name"],
                        "sol": branch["sol"],
                        "date": branch["date"],
                        "group_name": "NIL Sanction",
                        "declines": [
                            {
                                "parameter": f"{p} — NIL Sanction",
                                "actual": 0,
                                "target": 1,   # Nominal — the point is zero count, not an amount
                                "variance": -1,
                                "pct": 0.0,
                                "is_parent": True,
                            }
                            for p in branch["nil_params"]
                        ],
                    }
                    pdf = self.doc_service.generate_explanation_letter(payload)
                    zf.writestr(
                        f"Explanation_Letters/NIL_Sanction/Expl_{branch['sol']}_NIL_Sanction.pdf",
                        pdf,
                    )

        return zip_buffer.getvalue()

