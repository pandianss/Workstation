from __future__ import annotations

import io
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
        # Custom Premium Banking Styles
        self._init_custom_styles()

    def generate_office_note(self, department: str, subject: str, body: str, date: str | None = None, signatories: list[str] | None = None) -> str:
        """Generates a trilingual standard office note as HTML for preview."""
        template = self.env.get_template("office_note.html")
        return template.render(
            department=department,
            subject=subject,
            body=body,
            date=date or datetime.date.today().strftime("%d-%m-%Y"),
            signatories=signatories or ["Regional Manager"]
        )

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
        self.styles.add(ParagraphStyle(
            name='BankingHeader',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            textColor=colors.HexColor("#254aa0"),
            spaceAfter=2
        ))
        self.styles.add(ParagraphStyle(
            name='BankingSubHeader',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontSize=9,
            textColor=colors.HexColor("#475569"),
            spaceAfter=1
        ))
        self.styles.add(ParagraphStyle(
            name='OfficeNoteBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_LEFT
        ))
        self.styles.add(ParagraphStyle(
            name='SubjectLine',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            fontWeight='bold',
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=12
        ))

    def generate_pdf_note(self, department: str, subject: str, body: str, date: str | None = None, signatories: list[str] | None = None) -> bytes:
        """Generates a high-fidelity pure-python Banking Office Note via ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=50, bottomMargin=50)
        elements = []

        # 1. Official Header Section
        elements.append(Paragraph("इण्डियन ओवरसीज़ बैंक :: INDIAN OVERSEAS BANK", self.styles['BankingHeader']))
        elements.append(Paragraph("क्षेत्रीय कार्यालय, दिन्डिगुल :: REGIONAL OFFICE, DINDIGUL", self.styles['BankingSubHeader']))
        elements.append(Paragraph("மண்டல அலுவலகம், திண்டுக்கல்", self.styles['BankingSubHeader']))
        elements.append(Spacer(1, 0.2 * inch))

        # 2. Reference & Date
        date_val = date or datetime.date.today().strftime('%d-%m-%Y')
        ref_data = [
            [f"DEPT: {department.upper()}", f"DATE: {date_val}"]
        ]
        t_ref = Table(ref_data, colWidths=[3.5 * inch, 1.5 * inch])
        t_ref.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(t_ref)
        elements.append(Spacer(1, 0.1 * inch))

        # 3. Subject
        elements.append(Paragraph(f"<b>SUB: {subject.upper()}</b>", self.styles['SubjectLine']))

        # 4. Body Content
        elements.append(Paragraph(body.replace("\n", "<br/>"), self.styles['OfficeNoteBody']))
        elements.append(Spacer(1, 0.5 * inch))

        # 5. Signatories
        if signatories:
            sig_data = []
            for sig in signatories:
                sig_data.append([Paragraph(f"<b>({sig})</b>", self.styles['Normal']), "Regional Manager"])
            
            t_sig = Table(sig_data, colWidths=[2.5 * inch, 2.5 * inch])
            t_sig.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(t_sig)

        doc.build(elements)
        return buffer.getvalue()

    def generate_pdf_anniversary(self, branch_name: str, branch_code: str, anniversary_year: int) -> bytes:
        """Generates a celebratory anniversary note via ReportLab."""
        body = f"On the joyous occasion of the {anniversary_year}th Anniversary of {branch_name} ({branch_code}), the Regional Office extends its warmest congratulations and appreciation for the branch's consistent contribution to the region's growth."
        return self.generate_pdf_note(
            department="Regional Office",
            subject=f"Anniversary Congratulations: {branch_name}",
            body=body,
            signatories=["Regional Manager"]
        )
