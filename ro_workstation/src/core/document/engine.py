from __future__ import annotations
import io
import datetime
import base64
import subprocess
import tempfile
import os
import time
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader

from src.core.paths import project_path
from src.core.registry.parameter_service import ParameterRegistry

class DocumentEngine:
    """
    Unified engine for HTML-to-PDF generation.
    Handles templates, assets, and the headless browser interface.
    """
    def __init__(self, template_subdir: str = "") -> None:
        self.registry = ParameterRegistry()
        self.template_dir = project_path("src", "infrastructure", "templates")
        if template_subdir:
            self.template_dir = self.template_dir / template_subdir
            
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self._add_filters()
        
        self.assets_dir = project_path("src", "assets")
        self.fonts_dir = project_path("data", "fonts")
        self.org_data = self._load_org_data()

    def _add_filters(self):
        """Adds common Jinja2 filters for financial data with Indian formatting."""
        # Manual implementation for robustness
        
        def format_inr(value):
            try:
                if value is None: return "0.00"
                # Use robust formatting logic
                num = float(str(value).replace(',', '').replace('₹', '').replace(' ', '').strip() or 0)
                is_neg = num < 0
                num = abs(num)
                
                s = "{:.2f}".format(num)
                parts = s.split(".")
                int_part, dec_part = parts[0], parts[1]
                
                res = ""
                if len(int_part) <= 3:
                    res = int_part
                else:
                    res = int_part[-3:]
                    rem = int_part[:-3]
                    while len(rem) > 2:
                        res = rem[-2:] + "," + res
                        rem = rem[:-2]
                    if rem: res = rem + "," + res
                
                final = res + "." + dec_part
                return "-" + final if is_neg else final
            except:
                return str(value)
        
        def format_inr_k(value):
            try:
                if value is None: return "0"
                num = float(str(value).replace(',', '').replace('₹', '').replace(' ', '').strip() or 0)
                is_neg = num < 0
                num = abs(num)
                
                int_part = str(int(num))
                res = ""
                if len(int_part) <= 3:
                    res = int_part
                else:
                    res = int_part[-3:]
                    rem = int_part[:-3]
                    while len(rem) > 2:
                        res = rem[-2:] + "," + res
                        rem = rem[:-2]
                    if rem: res = rem + "," + res
                
                return "-" + res if is_neg else res
            except:
                return str(value)

        def format_date(value, fmt="%d.%m.%Y"):
            if not value: return ""
            if isinstance(value, str):
                try:
                    # Attempt to parse common formats
                    for f in ["%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
                        try:
                            value = datetime.datetime.strptime(value, f)
                            break
                        except: continue
                except: return value
            try:
                return value.strftime(fmt)
            except: return str(value)

        self.env.filters['format_inr'] = format_inr
        self.env.filters['format_inr_k'] = format_inr_k
        self.env.filters['format_date'] = format_date

    def _load_org_data(self) -> Dict[str, Any]:
        """Loads organizational metadata from registry with master data overrides."""
        org = self.registry.get_org_info()
        contact = self.registry.get_contact_info()
        
        # Format address with breaks
        def format_address(addr, marker):
            if not addr: return ""
            addr = str(addr).replace("<br/>", "").replace("<br>", "").replace("\n", " ").strip()
            addr = ", ".join([p.strip() for p in addr.split(",") if p.strip()])
            if marker in addr:
                parts = addr.split(marker, 1)
                return f"{parts[0]}{marker},<br/>{parts[1].lstrip(', ')}"
            return addr

        data = {
            "bankNameEn": org["bank_name"]["en"],
            "bankNameHi": org["bank_name"]["hi"],
            "bankNameTa": org["bank_name"]["ta"],
            "officeNameEn": org["office_name"]["en"],
            "officeNameHi": org["office_name"]["hi"],
            "officeNameTa": org["office_name"]["ta"],
            "addressEnFormatted": format_address(contact["address"]["en"], "Pensioner Street"),
            "addressHiFormatted": format_address(contact["address"]["hi"], "पेंशनर स्ट्रीट"),
            "addressTaFormatted": format_address(contact["address"]["ta"], "பென்ஷனர் தெரு"),
            "phone": contact["phone"],
            "email": contact["email"],
            "website": contact["website"],
            "headRoll": org.get("head_user_id")
        }

        # Load Logo
        logo_path = self.assets_dir / "doc_min.svg"
        if logo_path.exists():
            with logo_path.open("rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode('utf-8')
                data["bankLogo"] = f"data:image/svg+xml;base64,{logo_b64}"
                
        return data

    def render_doc(self, template_name: str, **kwargs) -> str:
        """Renders an HTML template with unified context."""
        template = self.env.get_template(template_name)
        
        # Inject standard context
        context = {
            "org": self.org_data,
            "font_base_url": self.fonts_dir.as_uri() + "/",
            "datetime": datetime,
            "today": datetime.date.today()
        }
        
        # Safely update with kwargs to avoid any internal clashes
        context.update(kwargs)
        
        return template.render(**context)

    def to_pdf(self, html: str) -> bytes:
        """Converts HTML to PDF using Headless Edge."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_file = os.path.join(tmp_dir, "input.html")
            pdf_file = os.path.join(tmp_dir, "output.pdf")
            
            # Ensure fonts are available to the converter
            if self.fonts_dir.exists():
                for font_file in self.fonts_dir.glob("*.ttf"):
                    shutil.copy(font_file, tmp_dir)
            
            # Make font URLs relative for the converter
            html = html.replace(self.fonts_dir.as_uri() + "/", "./")
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            infra = self.registry.get_infrastructure()
            edge_path = infra.get("browser_path", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
            
            cmd = [
                edge_path, "--headless=new", "--disable-gpu", "--no-sandbox",
                f"--print-to-pdf={pdf_file}", "--no-pdf-header-footer", html_file
            ]
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            try:
                subprocess.run(cmd, check=True, timeout=45, startupinfo=startupinfo)
                
                # Verify file writing
                for _ in range(20):
                    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 500:
                        break
                    time.sleep(0.5)
                
                with open(pdf_file, "rb") as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError(f"PDF generation failed: {str(e)}")

    def resolve_staff(self, identifier: str) -> Dict[str, Any]:
        """Resolve roll number or name to trilingual signatory details."""
        identifier = str(identifier)
        from src.application.services.master_service import DesignationMapper
        try:
            from src.infrastructure.persistence.master_repository import MasterRepository
            repo = MasterRepository()
            staff_records = repo.get_by_category("STAFF")
            found = next((s for s in staff_records if s.code == identifier or s.name_en == identifier or f"{s.name_en} ({s.metadata.get('designation')})" == identifier), None)
            if found:
                meta = found.metadata or {}
                
                # Prioritize metadata-based trilingual designations
                if meta.get("desig_hi") and meta.get("desig_ta"):
                    return {
                        "name": found.name_en, 
                        "name_hi": found.name_hi or found.name_en, 
                        "name_ta": found.name_local or found.name_en,
                        "roll": found.code, 
                        "desig_en": meta.get("desig_en", meta.get("designation", "Manager")),
                        "desig_hi": meta.get("desig_hi"), 
                        "desig_ta": meta.get("desig_ta")
                    }

                raw_desig = str(meta.get("designation", "")).upper()
                grade = str(meta.get("grade", "")).upper()
                
                # Precise IOB Grade-to-Designation Mapping
                if "VI" in grade: 
                    desig_key = "CHIEF REGIONAL MANAGER"
                elif "V" in grade and "IV" not in grade: 
                    desig_key = "SENIOR REGIONAL MANAGER"
                elif "IV" in grade: 
                    desig_key = "CHIEF MANAGER"
                else:
                    desig_key = None

                if desig_key:
                    trans = DesignationMapper.MAPPINGS[desig_key]
                    desig = {"en": desig_key.title(), "hi": trans["hi"], "ta": trans["ta"]}
                else:
                    desig = DesignationMapper.get_trilingual(raw_desig)

                return {
                    "name": found.name_en, "name_hi": found.name_hi or found.name_en, "name_ta": found.name_local or found.name_en,
                    "roll": found.code, "desig_en": desig["en"], "desig_hi": desig["hi"], "desig_ta": desig["ta"]
                }
        except: pass
        return {"name": identifier, "name_hi": identifier, "name_ta": identifier, "roll": "N/A", "desig_en": "Authorized Signatory", "desig_hi": "प्राधिकृत हस्ताक्षरकर्ता", "desig_ta": "அங்கீகரிக்கப்பட்ட கையொப்பமிட்டவர்"}
