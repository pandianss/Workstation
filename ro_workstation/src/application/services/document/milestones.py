from __future__ import annotations
import base64
from typing import Dict, Any
from src.core.document.engine import DocumentEngine
from src.core.paths import project_path

class MilestoneGenerator:
    """Generates celebratory and milestone-based documents."""
    def __init__(self, engine: DocumentEngine | None = None) -> None:
        self.engine = engine or DocumentEngine()

    def generate_anniversary_note(self, data: Dict[str, Any]) -> bytes:
        html = self.engine.render_doc(
            "anniversary_note.html",
            **data
        )
        return self.engine.to_pdf(html)

    def generate_staff_milestone(self, profile: Dict[str, Any], milestone_type: str, branch_name: str) -> bytes:
        # Load Photo if exists
        photo_url = ""
        photo_path = project_path("data", "staff_photos", f"{profile['roll']}.jpg")
        if photo_path.exists():
            with open(photo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                photo_url = f"data:image/jpeg;base64,{encoded}"

        # Resolve Logo
        logo_path = project_path("src", "assets", "2026logo_min.svg")
        logo_data = ""
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_data = f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode()}"

        html = self.engine.render_doc(
            "staff_milestone.html",
            logo_url=logo_data,
            milestone_type=milestone_type.upper(),
            name_en=profile["name"],
            name_ta=profile.get("name_ta", ""),
            designation=profile.get("desig_en", ""),
            branch_name=branch_name,
            photo_url=photo_url
        )
        return self.engine.to_pdf(html)

    def generate_appreciation_certificate(self, recipient: Dict[str, Any], reason: str, signatory: Dict[str, Any], date: str) -> bytes:
        html = self.engine.render_doc(
            "appreciation_certificate.html",
            recipient=recipient,
            reason=reason,
            signatory=signatory,
            date=date,
            ref_no=f"RO/DGL/CERT/{recipient['roll']}/{date[-4:]}"
        )
        return self.engine.to_pdf(html)
