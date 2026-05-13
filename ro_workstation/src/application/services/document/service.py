from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional
from src.core.document.engine import DocumentEngine

class DocumentService(DocumentEngine):
    """
    Refactored DocumentService that uses DocumentEngine.
    Maintained for backward compatibility and unified access.
    """
    def __init__(self) -> None:
        super().__init__()
        self.bank_founding_date = datetime.date(1937, 2, 10)

    def _html_to_pdf(self, html: str) -> bytes:
        return self.to_pdf(html)

    def _calculate_bank_years(self) -> int:
        today = datetime.date.today()
        years = today.year - self.bank_founding_date.year
        if (today.month, today.day) < (self.bank_founding_date.month, self.bank_founding_date.day):
            years -= 1
        return years

    def _render_template(self, template_name: str, **kwargs) -> str:
        # Inject legacy variables
        kwargs.setdefault("bank_years", self._calculate_bank_years())
        return self.render_doc(template_name, **kwargs)

    def _resolve_staff_profile(self, identifier: str) -> dict:
        return self.resolve_staff(identifier)

    # --- Unified Document Methods ---

    def generate_office_note(self, department: str, subject: str, intro_text: str, observations: str, recommendations: str, prepared_by: str = "Assistant", ref_no: str | None = None, date: str | None = None, signatories: list[str] | None = None, is_html: bool = False) -> str:
        initiator_profile = self._resolve_staff_profile(prepared_by)
        sig_profiles = [self._resolve_staff_profile(s) for s in (signatories or [])]
        
        context = {
            "department": department,
            "subject": subject,
            "intro_text": intro_text,
            "observations": observations,
            "recommendations": recommendations,
            "initiator": initiator_profile,
            "signatory_list": sig_profiles,
            "ref_no": ref_no or "RO/GEN/2026",
            "date": date or datetime.date.today().strftime("%d.%m.%Y"),
            "is_html": is_html
        }
        return self.render_doc("office_note.html", **context)

    def generate_pdf_note(self, *args, **kwargs) -> bytes:
        html = self.generate_office_note(*args, **kwargs)
        return self.to_pdf(html)

    def generate_anniversary_note(self, branch_name: str, branch_code: str, years: int, foundation_date: str | None = None, prepared_by: str | None = None) -> str:
        return self.render_doc("anniversary_note.html", branch_name=branch_name, branch_code=branch_code, anniversary_year=years, foundation_date=foundation_date, prepared_by=prepared_by or "Regional Office", date=datetime.date.today().strftime("%d.%m.%Y"))

    def generate_pdf_anniversary(self, *args, **kwargs) -> bytes:
        html = self.generate_anniversary_note(*args, **kwargs)
        return self.to_pdf(html)

    def generate_anniversary_poster(self, branch_name: str, years: int, open_date: str) -> bytes:
        template = self.env.get_template("anniversary_poster.html")
        html = template.render(
            logo_url=self.org_data.get("bankLogo", ""),
            branch_name=branch_name,
            years=years,
            open_date=open_date,
            region_name=self.org_data.get("region_name", "Regional Office")
        )
        return self.to_pdf(html)

    def generate_staff_milestone_html(self, staff_roll: str, milestone_type: str) -> str:
        from .milestones import MilestoneGenerator
        gen = MilestoneGenerator(self)
        from src.infrastructure.persistence.master_repository import MasterRepository
        repo = MasterRepository()
        staff_rec = next((s for s in repo.get_by_category("STAFF") if s.code == staff_roll), None)
        branch_name = "REGIONAL OFFICE"
        if staff_rec:
            sol = (staff_rec.metadata or {}).get("sol")
            unit = next((u for u in repo.get_by_category("UNIT") if u.code == sol), None)
            if unit: branch_name = unit.name_en
            
        profile = self.resolve_staff(staff_roll)
        return gen.generate_staff_milestone(profile, milestone_type, branch_name)

    def generate_high_value_dd_html(self, data: dict) -> str:
        from src.infrastructure.persistence.master_repository import MasterRepository
        repo = MasterRepository()
        sol = data.get("branch_sol", "")
        branch_rec = next((u for u in repo.get_by_category("UNIT") if u.code == sol), None)
        issuing_branch = branch_rec.name_en if branch_rec else f"Branch (SOL: {sol})"

        context = data.copy()
        context.pop("branch_sol", None) 
        context.update({
            "current_date": datetime.date.today().strftime("%d.%m.%Y"),
            "branch_sol": sol,
            "issuing_branch": issuing_branch,
        })
        return self.render_doc("high_value_dd.html", **context)

    def generate_high_value_dd_pdf(self, data: dict) -> bytes:
        html = self.generate_high_value_dd_html(data)
        return self.to_pdf(html)

    def generate_circular_pdf(self, circular_data: dict) -> bytes:
        from .operational import OperationalGenerator
        gen = OperationalGenerator(self)
        return gen.generate_circular(circular_data)

    def generate_performance_appreciation(self, performance: dict) -> bytes:
        from .performance import PerformanceGenerator
        gen = PerformanceGenerator(self)
        return gen.generate_appreciation(performance)

    def generate_explanation_letter(self, performance: dict) -> bytes:
        from .performance import PerformanceGenerator
        gen = PerformanceGenerator(self)
        return gen.generate_explanation(performance)

    def generate_budget_communication(self, payload: dict) -> bytes:
        from .performance import PerformanceGenerator
        gen = PerformanceGenerator(self)
        return gen.generate_budget_communication(payload)

    def generate_custom_letter_pdf(self, *args, **kwargs) -> bytes:
        from .operational import OperationalGenerator
        gen = OperationalGenerator(self)
        return gen.generate_custom_letter(kwargs)

    def generate_appreciation_certificate_pdf(self, recipient_roll: str, reason: str, signatory_roll: str, date: str = None) -> bytes:
        from .milestones import MilestoneGenerator
        gen = MilestoneGenerator(self)
        recipient = self.resolve_staff(recipient_roll)
        signatory = self.resolve_staff(signatory_roll)
        return gen.generate_appreciation_certificate(recipient, reason, signatory, date or datetime.date.today().strftime("%d.%m.%Y"))
