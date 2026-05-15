from __future__ import annotations
import base64
from typing import Dict, Any
from src.core.document.engine import DocumentEngine
from src.core.paths import project_path


def _staff_initials(name: str) -> str:
    parts = [part for part in str(name).replace(".", " ").split() if part]
    if not parts:
        return "IOB"
    if len(parts) == 1:
        return parts[0][:3].upper()
    return "".join(part[0] for part in parts[:3]).upper()

class MilestoneGenerator:
    """Generates celebratory and milestone-based documents."""
    def __init__(self, engine: DocumentEngine | None = None) -> None:
        self.engine = engine or DocumentEngine()

    def generate_anniversary_note_html(self, data: Dict[str, Any]) -> str:
        return self.engine.render_doc(
            "anniversary_note.html",
            **data
        )

    def generate_anniversary_note_pdf(self, data: Dict[str, Any]) -> bytes:
        html = self.generate_anniversary_note_html(data)
        return self.engine.to_pdf(html)

    def generate_anniversary_note(self, data: Dict[str, Any]) -> bytes:
        """Backward-compatible PDF API used by older document-centre code."""
        return self.generate_anniversary_note_pdf(data)

    def generate_staff_milestone_html(self, profile: Dict[str, Any], milestone_type: str, branch_name: str) -> str:
        # Load Assets
        assets = {}
        asset_files = {
            "logo_url": "2026logo_min.svg",
            "celebratory_bg": "birthday_bg.png",
            "celebratory_icon": "birthday_icon.png"
        }
        
        for key, filename in asset_files.items():
            path = project_path("src", "assets", filename)
            if path.exists():
                with open(path, "rb") as f:
                    mime = "image/svg+xml" if filename.endswith(".svg") else "image/png"
                    encoded = base64.b64encode(f.read()).decode()
                    assets[key] = f"data:{mime};base64,{encoded}"
            else:
                assets[key] = ""

        return self.engine.render_doc(
            "staff_milestone.html",
            milestone_type=milestone_type.upper(),
            name_en=profile["name"],
            name_ta=profile.get("name_ta", ""),
            designation=profile.get("desig_en", ""),
            branch_name=branch_name,
            **assets
        )

    def generate_staff_milestone_pdf(self, profile: Dict[str, Any], milestone_type: str, branch_name: str) -> bytes:
        html = self.generate_staff_milestone_html(profile, milestone_type, branch_name)
        return self.engine.to_pdf(html)

    def generate_staff_milestone(self, profile: Dict[str, Any], milestone_type: str, branch_name: str) -> bytes:
        """Backward-compatible PDF API used by older portal/service code."""
        return self.generate_staff_milestone_pdf(profile, milestone_type, branch_name)

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
