from __future__ import annotations

import io
import json
import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from jinja2 import Environment, FileSystemLoader
from src.core.paths import project_path


class DocumentService:
    def __init__(self) -> None:
        self.template_dir = project_path("src", "infrastructure", "templates")
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self.styles = getSampleStyleSheet()
        
        # Load Organization Metadata
        org_path = project_path("data", "organization.json")
        if org_path.exists():
            with org_path.open("r", encoding="utf-8") as f:
                self.org_data = json.load(f)
        else:
            self.org_data = {}

        # Custom Premium Banking Styles
        self._init_custom_styles()


    def draft_office_note_content(
        self,
        subject: str,
        department: str,
        brief: str,
        llm,  # LLMClient instance
        dept_system_prompt: str = "",
    ) -> dict:
        """
        Use the local LLM to draft intro, observations, and recommendations
        from a short user-provided brief. Returns a dict with keys:
        'introduction', 'observations', 'recommendations'.
        Raises ValueError if the LLM returns invalid JSON.
        """
        system = dept_system_prompt or (
            f"You are an expert AI assistant for the {department} department "
            "of an Indian Public Sector Bank Regional Office. "
            "You draft formal office notes in standard PSB format."
        )
        prompt = (
            f"Draft the body of a formal office note using the information below.\n\n"
            f"DEPARTMENT: {department}\n"
            f"SUBJECT: {subject}\n"
            f"BRIEF / KEY POINTS: {brief}\n\n"
            "Return ONLY a JSON object with exactly these three keys:\n"
            "{{\n"
            "  \"introduction\": \"<2–3 sentences: state the purpose and context formally>\",\n"
            "  \"observations\": \"<key observations as a single string; each point on a new line starting with '• '>\",\n"
            "  \"recommendations\": \"<1–2 sentences: formal recommendation for approval or action>\"\n"
            "}}\n\n"
            "Use formal Indian banking English. "
            "Do not add any text outside the JSON object."
        )
        return llm.generate_json(prompt, system)

    def generate_anniversary_note(self, branch_name: str, branch_code: str, anniversary_year: int) -> str:
        """Generates a celebratory anniversary note as HTML for preview."""
        template = self.env.get_template("anniversary_note.html")
        return template.render(
            branch_name=branch_name,
            branch_code=branch_code,
            anniversary_year=anniversary_year,
            date=datetime.date.today().strftime("%d-%m-%Y")
        )

    def _init_custom_styles(self):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # Define potential font paths (System & Local AppData)
        appdata_fonts = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
        system_fonts = "C:/Windows/Fonts"
        
        # 1. Register Tamil Font (Noto Serif Tamil)
        tamil_font_path = os.path.join(appdata_fonts, "NotoSerifTamil-VariableFont_wdth,wght.ttf")
        tamil_font_name = "NotoTamil"
        try:
            pdfmetrics.registerFont(TTFont(tamil_font_name, tamil_font_path))
        except:
            tamil_font_name = "Helvetica" # Fallback

        # 2. Register Hindi/Universal Font (Nirmala UI)
        hindi_font_path = os.path.join(system_fonts, "Nirmala.ttc")
        hindi_font_name = "Nirmala"
        try:
            # Index 0 in TTC is usually the main font
            pdfmetrics.registerFont(TTFont(hindi_font_name, hindi_font_path))
        except:
            hindi_font_name = "Helvetica"

        # 3. Create Styles using these fonts
        self.styles.add(ParagraphStyle(
            name='BankingHeader',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            fontName=hindi_font_name if hindi_font_name != "Helvetica" else "Helvetica-Bold",
            textColor=colors.HexColor("#00338d"),
            spaceAfter=2
        ))
        self.styles.add(ParagraphStyle(
            name='BankingSubHeader',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontSize=9,
            fontName=hindi_font_name,
            textColor=colors.HexColor("#475569"),
            spaceAfter=1
        ))
        self.styles.add(ParagraphStyle(
            name='OfficeNoteBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            fontName=tamil_font_name if tamil_font_name != "Helvetica" else hindi_font_name,
            alignment=TA_LEFT
        ))
        self.styles.add(ParagraphStyle(
            name='SubjectLine',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            fontName=hindi_font_name if hindi_font_name != "Helvetica" else "Helvetica-Bold",
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=12
        ))

    def generate_office_note(
        self,
        department: str,
        subject: str,
        intro_text: str,
        observations: str,
        recommendations: str,
        prepared_by: str = "Assistant",
        ref_no: str | None = None,
        date: str | None = None,
        signatories: list[str] | None = None
    ) -> str:
        """Generates a trilingual standard office note as HTML for preview."""
        template = self.env.get_template("office_note.html")
        return template.render(
            org=self.org_data,
            department=department,
            subject=subject,
            intro_text=intro_text,
            observations=observations,
            recommendations=recommendations,
            prepared_by=prepared_by,
            ref_no=ref_no or "RO/GEN/2026",
            date=date or datetime.date.today().strftime("%d-%m-%Y"),
            signatories=signatories or ["Regional Manager"]
        )

    def generate_pdf_note(
        self,
        department: str,
        subject: str,
        intro_text: str,
        observations: str,
        recommendations: str,
        prepared_by: str = "Assistant",
        ref_no: str | None = None,
        date: str | None = None,
        signatories: list[str] | None = None
    ) -> bytes:
        """Generates a high-fidelity trilingual Banking Office Note via ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=40)
        elements = []
        org = self.org_data

        # 1. Trilingual Header (Logo + 3 Bank Names)
        header_data = [
            [
                Paragraph(f"<font color='#00338d' size='14'><b>{org.get('bankNameTa', '')}</b></font>", self.styles['Normal']),
                "",
                ""
            ],
            [
                Paragraph(f"<font color='#00338d' size='12'><b>{org.get('bankNameHi', '')}</b></font>", self.styles['Normal']),
                "",
                ""
            ],
            [
                Paragraph(f"<font color='#00338d' size='13'><b>{org.get('bankNameEn', '')}</b></font>", self.styles['Normal']),
                "",
                ""
            ]
        ]
        t_head = Table(header_data, colWidths=[5 * inch, 0, 0])
        t_head.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(t_head)
        elements.append(Spacer(1, 0.1 * inch))
        
        # Horizontal Rule
        elements.append(Table([[""]], colWidths=[7.2 * inch], style=[('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor("#00338d"))]))
        elements.append(Spacer(1, 0.1 * inch))

        # 2. 3-Column Regional Office Info
        info_data = [
            [
                Paragraph(f"<b>{org.get('officeNameTa', '')}</b><br/>{org.get('addressTaFormatted', '')}", self.styles['Normal']),
                Paragraph(f"<b>{org.get('officeNameHi', '')}</b><br/>{org.get('addressHiFormatted', '')}", self.styles['Normal']),
                Paragraph(f"<b>{org.get('officeNameEn', '')}</b><br/>{org.get('addressEnFormatted', '')}", self.styles['Normal']),
            ]
        ]
        t_info = Table(info_data, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch])
        t_info.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.2, colors.lightgrey),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 0.15 * inch))

        # 3. Contact Strip
        contact_data = [[f"Phone: {org.get('phone', '')}", f"Email: {org.get('email', '')}", f"Web: {org.get('website', '')}"]]
        t_contact = Table(contact_data, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch])
        t_contact.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t_contact)
        elements.append(Spacer(1, 0.25 * inch))

        # 4. Meta Strip (Ref & Date)
        meta_data = [[f"REF NO: {ref_no or 'RO/GEN/2026'}", f"DATE: {date or datetime.date.today().strftime('%d-%m-%Y')}"]]
        t_meta = Table(meta_data, colWidths=[3.6 * inch, 3.6 * inch])
        t_meta.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 0.3 * inch))

        # 5. Document Title
        elements.append(Paragraph("OFFICE NOTE / कार्यालय टिप्पणी", self.styles['BankingHeader']))
        elements.append(Spacer(1, 0.2 * inch))

        # 6. Body Content
        elements.append(Paragraph(f"<b>SUBJECT: {subject.upper()}</b>", self.styles['SubjectLine']))
        
        elements.append(Paragraph("<b>1. Introduction</b>", self.styles['Normal']))
        elements.append(Paragraph(intro_text.replace("\n", "<br/>"), self.styles['OfficeNoteBody']))
        elements.append(Spacer(1, 0.15 * inch))

        elements.append(Paragraph("<b>2. Observations</b>", self.styles['Normal']))
        elements.append(Paragraph(observations.replace("\n", "<br/>"), self.styles['OfficeNoteBody']))
        elements.append(Spacer(1, 0.15 * inch))

        elements.append(Paragraph("<b>3. Recommendations</b>", self.styles['Normal']))
        elements.append(Paragraph(recommendations.replace("\n", "<br/>"), self.styles['OfficeNoteBody']))
        elements.append(Spacer(1, 0.5 * inch))

        # 7. Signatories
        sig_list = signatories or ["Regional Manager"]
        sig_data = [[
            Paragraph(f"Sd/-<br/><b>({prepared_by})</b><br/>Prepared By", self.styles['Normal']),
            "",
            Paragraph(f"Sd/-<br/><b>({sig_list[0]})</b><br/>Authorized Signatory", self.styles['Normal'])
        ]]
        t_sig = Table(sig_data, colWidths=[2.5 * inch, 2.2 * inch, 2.5 * inch])
        t_sig.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(t_sig)

        doc.build(elements)
        return buffer.getvalue()

    def generate_pdf_from_html(self, html: str) -> bytes:
        """Fallback for HTML-to-PDF pipeline (Simplified for ReportLab)."""
        # Since we don't have an HTML parser, we use a default structure
        return self.generate_pdf_note(
            department="Regional Office",
            subject="Automated Document",
            intro_text="This document was generated via the automated mail merge pipeline.",
            observations="See attached data manifest for details.",
            recommendations="Processing as per regional policy."
        )

    def generate_pdf_anniversary(self, branch_name: str, branch_code: str, anniversary_year: int) -> bytes:
        """Generates a celebratory anniversary note via ReportLab."""
        body = f"On the joyous occasion of the {anniversary_year}th Anniversary of {branch_name} ({branch_code}), the Regional Office extends its warmest congratulations and appreciation for the branch's consistent contribution to the region's growth."
        return self.generate_pdf_note(
            department="Regional Office",
            subject=f"Anniversary Congratulations: {branch_name}",
            intro_text=f"The Regional Office is pleased to note the {anniversary_year}th Anniversary of {branch_name} ({branch_code}).",
            observations="The branch has shown consistent growth and dedication to customer service.",
            recommendations="We extend our warmest congratulations and best wishes for continued success.",
            signatories=["Regional Manager"]
        )
