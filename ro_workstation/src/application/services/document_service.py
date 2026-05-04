from __future__ import annotations

import io
import json
import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from src.core.paths import project_path


def _font_base_url() -> str:
    """Returns an absolute file:// URL to the bundled fonts directory."""
    fonts_dir = project_path("data", "fonts")
    fonts_dir.mkdir(parents=True, exist_ok=True)
    return fonts_dir.as_uri() + "/"


class DocumentService:
    def __init__(self) -> None:
        self.template_dir = project_path("src", "infrastructure", "templates")
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Add custom filters for INR formatting
        def format_inr(value):
            try:
                if value is None: return "0.00"
                return "{:,.2f}".format(float(value))
            except:
                return str(value)
        
        def format_inr_k(value):
            try:
                if value is None: return "0"
                return "{:,.0f}".format(float(value))
            except:
                return str(value)

        self.env.filters['format_inr'] = format_inr
        self.env.filters['format_inr_k'] = format_inr_k
        self.bank_founding_date = datetime.date(1937, 2, 10)
        self.assets_dir = project_path("src", "assets")
        self.org_data = {}

        try:
            from src.infrastructure.persistence.master_repository import MasterRepository
            repo = MasterRepository()
            ro_record = next((r for r in repo.get_by_category("UNIT") if r.code == "3933"), None)
            
            def format_address(addr, marker):
                if not addr: return ""
                addr = str(addr)
                if marker in addr:
                    parts = addr.split(marker, 1)
                    return f"{parts[0]}{marker},<br/>{parts[1].lstrip(', ')}"
                return addr.replace(", ", ",<br/>")

            if ro_record:
                meta = ro_record.metadata or {}
                self.org_data = {
                    "bankNameEn": "INDIAN OVERSEAS BANK",
                    "bankNameHi": "इण्डियन ओवरसीज़ बैंक",
                    "bankNameTa": "இண்டியன் ஓவர்சீஸ் வங்கி",
                    "officeNameEn": ro_record.name_en or "REGIONAL OFFICE, DINDIGUL",
                    "officeNameHi": ro_record.name_hi or "क्षेत्रीय कार्यालय, डिंडिगुल",
                    "officeNameTa": ro_record.name_local or "மண்டல அலுவலகம், திண்டுக்கல்",
                    "addressEnFormatted": format_address(meta.get('address') or '80 Feet Road, Near Spencer Compound, Dindigul - 624001', "Dindigul"),
                    "addressHiFormatted": format_address(meta.get('addressHi') or '80 फीट रोड, स्पेंसर कंपाउंड के पास, डिंडीगुल - 624001', "डिंडीगुल"),
                    "addressTaFormatted": format_address(meta.get('addressTa') or '80 அடி சாலை, ஸ்பென்சர் காம்பவுண்ட் அருகில், திண்டுக்கல் - 624001', "திண்டுக்கல்"),
                    "phone": meta.get('phone', '0451-2422242'),
                    "email": meta.get('email', 'rodindigul@iob.in'),
                    "website": "www.iob.in",
                    "headRoll": str(meta.get('headUserId')) if meta.get('headUserId') else None
                }
        except Exception as e:
            print(f"Error initializing DocumentService: {e}")

        # Fallback to organization.json if units.csv didn't provide data
        if not self.org_data:
            org_path = project_path("data", "organization.json")
            if org_path.exists():
                with org_path.open("r", encoding="utf-8") as f:
                    self.org_data = json.load(f)

        # Load Logo as Base64 (src/assets/doc_min.svg) - SSOT for Branding
        import base64
        logo_path = project_path("src", "assets", "doc_min.svg")
        if logo_path.exists():
            with logo_path.open("rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode('utf-8')
                self.org_data["bankLogo"] = f"data:image/svg+xml;base64,{logo_b64}"

    # ── Internal: HTML → PDF via WeasyPrint (HarfBuzz shaping) ─────────────

    def _html_to_pdf(self, html: str) -> bytes:
        """
        Converts an HTML string to PDF bytes using Headless Microsoft Edge.
        This provides perfect rendering of complex scripts (Tamil/Hindi) 
        without requiring external GTK/Pango libraries.
        """
        import subprocess
        import tempfile
        import os
        import time
        import shutil

        # Create temporary directory for the conversion
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_file = os.path.join(tmp_dir, "input.html")
            pdf_file = os.path.join(tmp_dir, "output.pdf")
            
            # Copy all fonts to the temp directory to ensure local loading works
            fonts_src = project_path("data", "fonts")
            if fonts_src.exists():
                for font_file in fonts_src.glob("*.ttf"):
                    shutil.copy(font_file, tmp_dir)
            
            # Write HTML to temp file
            # Note: We must re-render or fix the font_base_url to be relative now
            # Since the HTML was already rendered with absolute file:// URLs, 
            # we'll do a quick string replacement to make it relative.
            html = html.replace(_font_base_url(), "./")
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            # Paths to Edge executable (standard Windows location)
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            
            # Command to run Edge in headless mode for printing
            # Using --headless=new for better stability in modern Chromium
            cmd = [
                edge_path,
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--run-all-compositor-stages-before-draw",
                "--allow-file-access-from-files",
                f"--print-to-pdf={pdf_file}",
                "--no-pdf-header-footer",
                "--no-first-run",
                "--no-default-browser-check",
                html_file
            ]
            
            # Windows-specific: Hide the console window
            startupinfo = None
            if os.name == 'nt':
                import subprocess as sp
                startupinfo = sp.STARTUPINFO()
                startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = sp.SW_HIDE

            try:
                # Run the command with an increased timeout
                process = subprocess.run(
                    cmd, 
                    check=True, 
                    timeout=45, 
                    capture_output=True,
                    startupinfo=startupinfo
                )
                
                # Wait a tiny bit for file to be released/written
                for _ in range(30):
                    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 500:
                        break
                    time.sleep(0.5)
                
                if not os.path.exists(pdf_file):
                    raise FileNotFoundError(f"Edge finished but output PDF was not created. Error: {process.stderr.decode(errors='replace')}")
                
                with open(pdf_file, "rb") as f:
                    return f.read()
            except subprocess.TimeoutExpired:
                # Attempt to kill any orphaned Edge processes
                if os.name == 'nt':
                    os.system("taskkill /f /im msedge.exe /fi \"status eq running\" >nul 2>&1")
                raise RuntimeError("PDF generation timed out. Please try again. Background processes have been cleared.")
            except Exception as e:
                raise RuntimeError(f"PDF generation via Edge failed: {str(e)}")

    def _calculate_bank_years(self) -> int:
        """Calculates completed years since foundation (10.02.1937)."""
        today = datetime.date.today()
        years = today.year - self.bank_founding_date.year
        if (today.month, today.day) < (self.bank_founding_date.month, self.bank_founding_date.day):
            years -= 1
        return years

    def _render_template(self, template_name: str, **kwargs) -> str:
        """Render a Jinja2 template with org data and font URL injected."""
        template = self.env.get_template(template_name)
        
        # Inject Beti Logo if available
        beti_logo = self.assets_dir / "beti.png"
        if beti_logo.exists():
            self.org_data["betiLogo"] = f"file:///{beti_logo.as_posix()}"
        
        return template.render(
            org=self.org_data,
            font_base_url=_font_base_url(),
            bank_years=self._calculate_bank_years(),
            datetime=datetime,
            **kwargs,
        )

    def _resolve_staff_profile(self, identifier: str) -> dict:
        """Resolve roll number or name to trilingual signatory details."""
        identifier = str(identifier)
        DESIG_MAP = {
            "REGIONAL MANAGER": {"en": "Regional Manager", "hi": "क्षेत्रीय प्रबंधक", "ta": "மண்டல மேலாளர்"},
            "SENIOR REGIONAL MANAGER": {"en": "Senior Regional Manager", "hi": "वरिष्ठ क्षेत्रीय प्रबंधक", "ta": "முதன்மை மண்டல மேலாளர்"},
            "CHIEF REGIONAL MANAGER": {"en": "Chief Regional Manager", "hi": "मुख्य क्षेत्रीय प्रबंधक", "ta": "தலைமை மண்டல மேலாளர்"},
            "CHIEF MANAGER": {"en": "Chief Manager", "hi": "मुख्य प्रबंधक", "ta": "முதன்மை மேலாளர்"},
            "SENIOR MANAGER": {"en": "Senior Manager", "hi": "वरिष्ठ प्रबंधक", "ta": "மூத்த மேலாளர்"},
            "MANAGER": {"en": "Manager", "hi": "प्रबंधक", "ta": "மேலாளர்"},
        }
        try:
            from src.infrastructure.persistence.master_repository import MasterRepository
            repo = MasterRepository()
            staff_records = repo.get_by_category("STAFF")
            found = next((s for s in staff_records if s.code == identifier or s.name_en == identifier or f"{s.name_en} ({s.metadata.get('designation')})" == identifier), None)
            if found:
                meta = found.metadata or {}
                raw_desig = str(meta.get("designation", "")).upper()
                grade = str(meta.get("grade", "")).upper()
                
                # Precise IOB Grade-to-Designation Mapping
                if "VI" in grade: # Scale VI - Chief Regional Manager
                    desig = DESIG_MAP["CHIEF REGIONAL MANAGER"]
                elif "V" in grade and "IV" not in grade: # Scale V - Senior Regional Manager
                    desig = DESIG_MAP["SENIOR REGIONAL MANAGER"]
                elif "IV" in grade: # Scale IV - Chief Manager
                    desig = DESIG_MAP["CHIEF MANAGER"]
                else:
                    matched_key = next((k for k in DESIG_MAP if k in raw_desig), "REGIONAL MANAGER")
                    desig = DESIG_MAP[matched_key]
                return {
                    "name": found.name_en, "name_hi": found.name_hi or found.name_en, "name_ta": found.name_local or found.name_en,
                    "roll": found.code, "desig_en": desig["en"], "desig_hi": desig["hi"], "desig_ta": desig["ta"]
                }
        except: pass
        return {"name": identifier, "name_hi": identifier, "name_ta": identifier, "roll": "N/A", "desig_en": "Authorized Signatory", "desig_hi": "प्राधिकृत हस्ताक्षरकर्ता", "desig_ta": "அங்கீகரிக்கப்பட்ட கையொப்பமிட்டவர்"}

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
        return self._render_template("office_note.html", **context)

    def generate_anniversary_note(self, branch_name: str, branch_code: str, years: int, foundation_date: str | None = None, prepared_by: str | None = None) -> str:
        return self._render_template("anniversary_note.html", branch_name=branch_name, branch_code=branch_code, anniversary_year=years, foundation_date=foundation_date, prepared_by=prepared_by or "Regional Office", date=datetime.date.today().strftime("%d-%m-%Y"))

    def generate_pdf_note(self, department: str, subject: str, intro_text: str, observations: str, recommendations: str, prepared_by: str = "Assistant", ref_no: str | None = None, date: str | None = None, signatories: list[str] | None = None, is_html: bool = False) -> bytes:
        html = self.generate_office_note(department, subject, intro_text, observations, recommendations, prepared_by, ref_no, date, signatories, is_html=is_html)
        return self._html_to_pdf(html)

    def generate_pdf_anniversary(self, branch_name: str, branch_code: str, years: int, foundation_date: str | None = None, prepared_by: str | None = None) -> bytes:
        html = self.generate_anniversary_note(branch_name, branch_code, years, foundation_date, prepared_by)
        return self._html_to_pdf(html)

    def _get_signatory(self, roll_no: str) -> dict:
        return self._resolve_staff_profile(roll_no)

    def generate_circular_pdf(self, circular_data: dict) -> bytes:
        """Generates a regional circular with trilingual signatory."""
        author_roll = circular_data.get("author") or self.org_data.get("headRoll") or "63039"
        signatory = self._get_signatory(author_roll)
        
        # Format date as dd.mm.yyyy
        raw_date = circular_data.get("date")
        if isinstance(raw_date, (datetime.date, datetime.datetime)):
            date_obj = raw_date
        elif isinstance(raw_date, str):
            try:
                date_obj = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
            except:
                try:
                    date_obj = datetime.datetime.strptime(raw_date, "%d-%m-%Y").date()
                except:
                    date_obj = datetime.date.today()
        else:
            date_obj = datetime.date.today()
            
        formatted_date = date_obj.strftime("%d.%m.%Y")
        
        html = self._render_template(
            "circular.html",
            subject=circular_data.get("subject", "Circular"),
            body=circular_data.get("body", ""),
            conclusion=circular_data.get("conclusion", ""),
            ref_no=circular_data.get("ref_no", "RO/MIS/2026"),
            date=formatted_date,
            author=signatory["name"],
            roll=signatory["roll"],
            sig=signatory,
            is_html=circular_data.get("is_html", False)
        )
        return self._html_to_pdf(html)

    def generate_milestones_pdf(self, milestone_data: list, summary_data: list, selected_date: str) -> bytes:
        """Generates a PDF report for business milestones."""
        # milestone_data is a list of {"branch_name", "parameter", "value", "milestone"}
        # Sort by value descending
        achievements = sorted(milestone_data, key=lambda x: x["value"], reverse=True)[:15]
        
        html = self._render_template(
            "milestones_report.html",
            summary=summary_data,
            achievements=achievements,
            selected_date=selected_date,
            ref_no="RO/MIS/MIL/2026",
            date=datetime.date.today().strftime("%d.%m.%Y"),
            prepared_by=self.org_data.get("officeNameEn", "Regional Office")
        )
        return self._html_to_pdf(html)

    def generate_appreciation_letter(self, achievement: dict) -> bytes:
        """Generates an appreciation letter for a specific breakthrough."""
        import datetime
        month_year = achievement["date"].strftime("%B %Y")
        
        # Resolve Region Head as Signatory
        head_roll = self.org_data.get("headRoll") or "63039"
        signatory = self._resolve_staff_profile(head_roll)
        
        html = self._render_template(
            "appreciation_letter.html",
            branch_name=achievement["branch_name"],
            sol=achievement["sol"],
            parameter=achievement["parameter"],
            milestone=achievement["milestone"],
            month_year=month_year,
            achievement_date=achievement["date"].strftime("%d.%m.%Y"),
            signatory=signatory,
            ref_no=f"RO/DGL/APPR/{achievement['sol']}/2026",
            date=datetime.date.today().strftime("%d.%m.%Y")
        )
        return self._html_to_pdf(html)

    def generate_performance_appreciation(self, performance: dict) -> bytes:
        """Generates a letter for budget target achievements."""
        month_year = performance["date"].strftime("%B %Y")
        head_roll = self.org_data.get("headRoll") or "63039"
        signatory = self._resolve_staff_profile(head_roll)
        
        html = self._render_template(
            "performance_appreciation.html",
            branch_name=performance["branch_name"],
            sol=performance["sol"],
            achievements=performance["achievements"],
            group_name=performance.get("group_name", "Budget"),
            month_year=month_year,
            signatory=signatory,
            ref_no=f"RO/DGL/MIS/ACH/{performance['sol']}/2026",
            date=datetime.date.today().strftime("%d.%m.%Y")
        )
        return self._html_to_pdf(html)

    def generate_explanation_letter(self, performance: dict) -> bytes:
        """Generates an explanation letter for budget shortfalls."""
        month_year = performance["date"].strftime("%B %Y")
        head_roll = self.org_data.get("headRoll") or "63039"
        signatory = self._resolve_staff_profile(head_roll)
        
        html = self._render_template(
            "explanation_letter.html",
            branch_name=performance["branch_name"],
            sol=performance["sol"],
            declines=performance["declines"],
            group_name=performance.get("group_name", "Budget"),
            month_year=month_year,
            signatory=signatory,
            ref_no=f"RO/DGL/MIS/EXP/{performance['sol']}/2026",
            date=datetime.date.today().strftime("%d.%m.%Y")
        )
        return self._html_to_pdf(html)

    def generate_branch_visit_report(self, month: int, year: int, visits: list) -> bytes:
        """Generates a consolidated monthly branch visit return."""
        month_name = datetime.date(year, month, 1).strftime("%B").upper()
        html = self._render_template(
            "branch_visit_report.html",
            month_name=month_name,
            year=year,
            visits=visits
        )
        return self._html_to_pdf(html)

    def generate_visit_observation_letter(self, visit: dict | Any) -> bytes:
        """Generates an individual observation letter to a branch manager."""
        # Handle both dict and SQLAlchemy model
        if hasattr(visit, "__table__"):
            v_data = {
                "branch_name": visit.branch_name,
                "sol": visit.sol,
                "visitor_name": visit.visitor_name,
                "visit_date": visit.visit_date,
                "observations": visit.observations,
                "advice": visit.advice_to_branch
            }
        else:
            v_data = visit

        head_roll = self.org_data.get("headRoll") or "63039"
        signatory = self._resolve_staff_profile(head_roll)
        
        html = self._render_template(
            "visit_observation_letter.html",
            branch_name=v_data["branch_name"],
            sol=v_data["sol"],
            visitor_name=v_data["visitor_name"],
            visit_date=v_data["visit_date"],
            observations=v_data["observations"],
            advice=v_data["advice"],
            signatory=signatory
        )
        return self._html_to_pdf(html)

    def generate_dicgc_return(self, data: dict) -> bytes:
        """Generates the DICGC Certificate of Confirmation."""
        head_roll = self.org_data.get("headRoll") or "63039"
        signatory = self._resolve_staff_profile(head_roll)
        
        html = self._render_template(
            "dicgc_return.html",
            as_on_date=data["as_on_date"],
            central_govt_amt=data["central_govt_amt"],
            state_govt_amt=data["state_govt_amt"],
            inter_bank_amt=data["inter_bank_amt"],
            ro_name=self.org_data.get("officeNameEn", "DINDIGUL"),
            ro_location=self.org_data.get("officeNameEn", "DINDIGUL").split(",")[-1].strip(),
            signatory=signatory
        )
        return self._html_to_pdf(html)

    def generate_dicgc_form_di01(self, data: dict) -> bytes:
        """Generates the official DICGC Form DI-01."""
        html = self._render_template(
            "dicgc_form_di01.html",
            **data
        )
        return self._html_to_pdf(html)

    def generate_wizard_pdf(self, wizard_type: str, data: dict, submitted_by: str, subject: str = None, ref: str = None) -> bytes:
        """Generates a generic report for any wizard submission."""
        title_map = {
            "broken_interest": "Broken Period Interest Calculation",
            "rbi_proforma": "RBI Proforma Reporting",
            "expense_approval": "Administrative Expense Approval",
            "gl_activation": "GL Head Activation Request",
            "high_value_dd": "High Value DD Reporting",
            "micr_request": "MICR/Cheque Book Request",
            "proforma_branch": "Proforma Branch Code Capture",
            "reversal_charges": "Reversal of Charges / Waiver Request"
        }
        
        # Use specialized template for broken interest if preferred, else generic
        template = "wizard_generic.html"
        if wizard_type == "broken_interest":
            template = "wizard_broken_interest.html"
            
        html = self._render_template(
            template,
            title=subject or title_map.get(wizard_type, wizard_type.replace('_', ' ').title()),
            data=data,
            submitted_by=submitted_by,
            reference_no=ref,
            date=datetime.date.today().strftime("%d.%m.%Y"),
            **data # Unpack data for specialized templates
        )
        return self._html_to_pdf(html)

