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
        "Core Retail": ["Core Retail", "Housing", "Vehicle", "Personal", "Mortgage", "Education", "Liquirent", "Other Retail"],
        "MSME": ["MSME", "Mudra", "SHG"],
        "Core Agri": ["Core Agri", "Gold", "KCC", "Agri JL"]
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
        """Generates a zip of PDFs for appreciation and explanation letters."""
        import io
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for branch in performance_data:
                # 1. Appreciation Letter for achievements
                if branch["achievements"]:
                    pdf = self.doc_service.generate_performance_appreciation(branch)
                    pdf_name = f"Appreciation_{branch['branch_name'].replace(' ', '_')}_{branch['sol']}.pdf"
                    zf.writestr(f"Appreciation_Letters/{pdf_name}", pdf)

                # 2. Explanation Letter if significant shortfalls
                if branch["declines"]:
                    pdf = self.doc_service.generate_explanation_letter(branch)
                    pdf_name = f"Explanation_{branch['branch_name'].replace(' ', '_')}_{branch['sol']}.pdf"
                    zf.writestr(f"Explanation_Letters/{pdf_name}", pdf)
        
        return zip_buffer.getvalue()
