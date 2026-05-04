from __future__ import annotations
import datetime
from typing import Dict, List, Any
import pandas as pd
from src.infrastructure.persistence.budget_repository import BudgetRepository
from src.application.use_cases.mis.service import MISAnalyticsService
from src.application.services.document_service import DocumentService

class PerformanceLetterService:
    """Service to generate appreciation and explanation letters based on budget performance."""
    
    PARAM_GROUPS = {
        "Deposits": ["Total Deposits", "CASA", "SB", "CD", "Ret TD"],
        "Core Retail": ["Core Retail", "Housing", "Vehicle", "Personal", "Education", "Mortgage", "Liquirent", "Other Retail"],
        "MSME": ["MSME", "Mudra", "SHG"],
        "Core Agri": ["Core Agri", "SHG", "KCC", "Gov", "OthSch"],
        "Jewel Loan": ["Gold", "Agri JL", "Ret-Gold"]
    }

    def __init__(self):
        self.analytics_service = MISAnalyticsService()
        self.budget_repo = BudgetRepository()
        self.doc_service = DocumentService()

    def get_branch_performance(self, selected_date: datetime.date) -> List[Dict[str, Any]]:
        """Analyzes all branches for budget achievement or decline."""
        df = self.analytics_service.get_data()
        if df.empty:
            return []
            
        current_month_df = df[df["DATE"].dt.date == selected_date]
        if current_month_df.empty:
            return []

        results = []
        for _, row in current_month_df.iterrows():
            sol = int(row["SOL"])
            if sol == 3933: continue # Skip RO
            
            branch_performance = {
                "sol": sol,
                "branch_name": row.get("BRANCH", f"SOL {sol}"),
                "date": selected_date,
                "achievements": [],
                "declines": []
            }

            # Check each parameter against budget
            for group_name, params in self.PARAM_GROUPS.items():
                for p in params:
                    actual = row.get(p.upper(), row.get(p, 0.0))
                    # Budget is typically stored in Lacs in MIS but maybe Cr in Budget?
                    # The budget_repo handles mapping.
                    target = self.budget_repo.get_target(p, selected_date.strftime("%Y-%m"), sols=[sol])
                    
                    if target > 0:
                        variance = actual - target
                        achievement_pct = (actual / target * 100)
                        
                        if achievement_pct >= 100:
                            branch_performance["achievements"].append({
                                "parameter": p,
                                "actual": actual,
                                "target": target,
                                "variance": variance,
                                "pct": achievement_pct
                            })
                        elif achievement_pct < 90: # Significant decline/shortfall
                            branch_performance["declines"].append({
                                "parameter": p,
                                "actual": actual,
                                "target": target,
                                "variance": variance,
                                "pct": achievement_pct
                            })
            
            if branch_performance["achievements"] or branch_performance["declines"]:
                results.append(branch_performance)
                
        return results

    def generate_letters_zip(self, performance_data: List[Dict[str, Any]]) -> bytes:
        """Generates a zip of PDFs for appreciation and explanation letters, grouped by parameter category."""
        import io
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for branch in performance_data:
                # Group branch achievements and declines by PARAM_GROUPS
                branch_groups = {}
                for group_name, params in self.PARAM_GROUPS.items():
                    branch_groups[group_name] = {
                        "achievements": [a for a in branch["achievements"] if a["parameter"] in params],
                        "declines": [d for d in branch["declines"] if d["parameter"] in params]
                    }

                for group_name, data in branch_groups.items():
                    # 1. Group Appreciation Letter
                    if data["achievements"]:
                        perf_payload = {
                            "branch_name": branch["branch_name"],
                            "sol": branch["sol"],
                            "date": branch["date"],
                            "group_name": group_name,
                            "achievements": data["achievements"]
                        }
                        pdf = self.doc_service.generate_performance_appreciation(perf_payload)
                        folder = f"Appreciation_Letters/{group_name.replace(' ', '_')}"
                        file_name = f"Appr_{branch['sol']}_{group_name.replace(' ', '_')}.pdf"
                        zf.writestr(f"{folder}/{file_name}", pdf)

                    # 2. Group Explanation Letter
                    if data["declines"]:
                        perf_payload = {
                            "branch_name": branch["branch_name"],
                            "sol": branch["sol"],
                            "date": branch["date"],
                            "group_name": group_name,
                            "declines": data["declines"]
                        }
                        pdf = self.doc_service.generate_explanation_letter(perf_payload)
                        folder = f"Explanation_Letters/{group_name.replace(' ', '_')}"
                        file_name = f"Expl_{branch['sol']}_{group_name.replace(' ', '_')}.pdf"
                        zf.writestr(f"{folder}/{file_name}", pdf)
        
        return zip_buffer.getvalue()
