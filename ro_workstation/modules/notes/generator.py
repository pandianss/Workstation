import html
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.identity import DEFAULT_NOTE_CONTEXT, RO_BLUE, UNICODE_FONT
from app.services.report_service import draw_ro_template

from ..llm.client import LLMClient
from ..utils.paths import project_path


class NoteGenerator:
    def __init__(self):
        self.llm = LLMClient()

    def generate_note(self, template: str, subject: str, data_points: str, dept: str) -> str:
        """Generates a free-form text note using LLM."""
        prompt = f"Draft an office note based on template '{template}'. Subject: {subject}. Key points: {data_points}."
        system_prompt = (
            f"You are a professional bank officer in the {dept} department. "
            "Output the note in standard PSB format (Ref No / Date / To / Subject / Background / Analysis / Recommendations / Approval sought)."
        )

        return self.llm.generate(prompt, system_prompt)

    def generate_html_note(self, template_type: str, raw_data: str) -> str:
        """Extracts data and renders an HTML preview for the workstation UI."""
        if template_type == "Payment of Bills":
            payload = self._extract_payment_note_payload(raw_data)
            return self._render_office_note_html(payload)

        return "<div>Template not found</div>"

    def generate_pdf_note(self, template_type: str, raw_data: str) -> bytes:
        """Generates a high-fidelity PDF using reportlab, unified with RO stationery."""
        if template_type == "Payment of Bills":
            payload = self._extract_payment_note_payload(raw_data)
            return self._render_office_note_pdf(payload)
        
        # Fallback for generic notes
        return self._render_generic_pdf(template_type, raw_data)

    def _extract_payment_note_payload(self, raw_data: str) -> dict:
        schema = {
            "ref_no": "RO/DGL/PLNG/2026-27/05/04",
            "date": "DD.MM.YYYY",
            "subject": "PAYMENT OF BILLS - SUBJECT DETAILS",
            "department_en": "Planning Department",
            "department_hi": "योजना विभाग",
            "department_ta": "திட்டமிடல் துறை",
            "vendor_name": "Vendor Name",
            "vendor_code": "VENDOR123",
            "intro_text": "Vendor has presented a bill for services availed. Details are as follows:",
            "line_items": [
                {
                    "s_no": "1",
                    "date": "DD.MM.YYYY",
                    "details": "Description",
                    "amount": 1000,
                    "rate": "100/pc",
                }
            ],
            "total": "1000",
            "summary_rows": [
                {"label": "Ro Budget", "value": "Rs 20,00,000/-"},
                {"label": "Utilised so far", "value": "Rs 38,696/-"},
            ],
            "recommendation_heading": "Department Observation & Recommendations",
            "recommendation_paragraphs": [
                "Since the aforementioned services were utilised for official purposes, we may make payment to the vendor."
            ],
        }

        prompt = (
            "Extract structured office-note data from the following raw input. "
            "Normalize the output for a bank office-note format and preserve table rows where available.\n\n"
            f"{raw_data}"
        )
        system_prompt = (
            "You are an expert banking document data extractor. "
            f"Return ONLY valid JSON matching this schema: {schema}"
        )
        data = self.llm.generate_json(prompt, system_prompt)

        # Fallback for offline/errors
        if data.get("status") == "offline_stub" or data.get("error"):
            data = {
                "ref_no": "RO/DGL/PLNG/2026-27/05/04",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "subject": "PAYMENT OF BILLS - DRAFT (FALLBACK)",
                "vendor_name": "Regional Vendors",
                "intro_text": "Extraction failed. Using raw data summary as fallback.",
                "line_items": [{"s_no": "1", "date": datetime.now().strftime("%d.%m.%Y"), "details": "Manual Entry Required", "amount": 0, "rate": "-"}],
                "total": "0",
                "summary_rows": [],
                "recommendation_paragraphs": ["Review raw data manually before approval."]
            }

        payload = {**DEFAULT_NOTE_CONTEXT, **data}
        return payload

    def _render_office_note_html(self, payload: dict) -> str:
        template_path = project_path("modules", "notes", "templates", "payment_note.html")
        with template_path.open("r", encoding="utf-8") as f:
            html_template = f.read()

        replacements = {
            "{{office_name_ta}}": self._escape(payload.get("office_name_ta", "")),
            "{{office_name_hi}}": self._escape(payload.get("office_name_hi", "")),
            "{{office_name_en}}": self._escape(payload.get("office_name_en", "")),
            "{{address_ta}}": self._escape(payload.get("address_ta", "")),
            "{{address_hi}}": self._escape(payload.get("address_hi", "")),
            "{{address_en}}": self._escape(payload.get("address_en", "")),
            "{{contact_line}}": self._escape(payload.get("contact_line", "")),
            "{{department_ta}}": self._escape(payload.get("department_ta", "")),
            "{{department_hi}}": self._escape(payload.get("department_hi", "")),
            "{{department_en}}": self._escape(payload.get("department_en", "")),
            "{{note_label_ta}}": self._escape(payload.get("note_label_ta", "")),
            "{{note_label_hi}}": self._escape(payload.get("note_label_hi", "")),
            "{{note_label_en}}": self._escape(payload.get("note_label_en", "")),
            "{{date}}": self._escape(payload.get("date", "")),
            "{{ref_no}}": self._escape(payload.get("ref_no", "")),
            "{{salutation}}": self._escape(payload.get("salutation", "")),
            "{{subject}}": self._escape(payload.get("subject", "")),
            "{{intro_html}}": self._paragraph_html(payload.get("intro_text", ""), bold_vendor=payload.get("vendor_name")),
            "{{line_items_html}}": self._build_line_items_html(payload.get("line_items", [])),
            "{{total}}": self._escape(str(payload.get("total", ""))),
            "{{summary_rows_html}}": self._build_summary_rows_html(payload.get("summary_rows", [])),
            "{{recommendation_heading}}": self._escape(payload.get("recommendation_heading", "")),
            "{{recommendation_html}}": self._build_recommendation_html(payload.get("recommendation_paragraphs", [])),
            "{{signature_blocks_html}}": self._build_signature_blocks_html(payload.get("signature_blocks", [])),
        }

        for key, value in replacements.items():
            html_template = html_template.replace(key, value)
        return html_template

    def _render_office_note_pdf(self, payload: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1.5*inch, bottomMargin=1*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle('NoteHeader', parent=styles['Normal'], fontName=UNICODE_FONT, fontSize=11, alignment=1, spaceAfter=10)
        subject_style = ParagraphStyle('NoteSubject', parent=styles['Normal'], fontName=UNICODE_FONT, fontSize=12, alignment=1, leading=15, spaceBefore=10, spaceAfter=15)
        body_style = ParagraphStyle('NoteBody', parent=styles['Normal'], fontName=UNICODE_FONT, fontSize=10, leading=13, spaceAfter=8)
        
        # 1. Dept and Note Label
        meta_data = [
            [
                Paragraph(f"<b>{payload['department_ta']} / {payload['department_hi']} / {payload['department_en']}</b><br/>"
                          f"<b>{payload['note_label_ta']} / {payload['note_label_hi']} / {payload['note_label_en']}</b>", body_style),
                Paragraph(f"<b>Date:</b> {payload['date']}<br/>{payload['ref_no']}", ParagraphStyle('RightMeta', parent=body_style, alignment=2))
            ]
        ]
        meta_table = Table(meta_data, colWidths=[4.5*inch, 2.5*inch])
        meta_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#d9e2f3')),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # 2. Salutation and Subject
        elements.append(Paragraph(payload['salutation'], body_style))
        elements.append(Paragraph(f"<u>{payload['subject']}</u>", subject_style))
        
        # 3. Intro
        elements.append(Paragraph(payload['intro_text'], body_style))
        
        # 4. Line Items Table
        line_items = [["S No", "Date", "Details", "Amount (Rs)", "Rate"]]
        for item in payload.get("line_items", []):
            line_items.append([item.get("s_no", ""), item.get("date", ""), item.get("details", ""), str(item.get("amount", "")), item.get("rate", "")])
        line_items.append(["", "", "Total", str(payload.get("total", "")), ""])
        
        lt = Table(line_items, colWidths=[0.5*inch, 1*inch, 3*inch, 1.2*inch, 1.3*inch])
        lt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9e2f3')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), UNICODE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(lt)
        elements.append(Spacer(1, 0.2*inch))
        
        # 5. Summary Rows (Budget etc)
        if payload.get("summary_rows"):
            summary_data = [[r.get("label", ""), r.get("value", "")] for r in payload["summary_rows"]]
            st = Table(summary_data, colWidths=[2.5*inch, 4.5*inch])
            st.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), UNICODE_FONT),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef2ff')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements.append(st)
            elements.append(Spacer(1, 0.2*inch))
        
        # 6. Recommendations
        elements.append(Paragraph(f"<i>{payload['recommendation_heading']}</i>", body_style))
        for p in payload.get("recommendation_paragraphs", []):
            elements.append(Paragraph(p, body_style))
            
        # 7. Signatures
        sig_data = [[]]
        for block in payload.get("signature_blocks", []):
            sig_text = (f"({block.get('name_ta')} / {block.get('name_hi')} / {block.get('name_en')})<br/>"
                        f"{block.get('designation_ta')} / {block.get('designation_hi')} / {block.get('designation_en')}")
            sig_data[0].append(Paragraph(sig_text, ParagraphStyle('Sig', parent=body_style, alignment=1, fontSize=8)))
        
        sig_table = Table(sig_data, colWidths=[2.33*inch]*len(sig_data[0]))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(sig_table)
        
        doc.build(elements, onFirstPage=draw_ro_template, onLaterPages=draw_ro_template)
        buffer.seek(0)
        return buffer.getvalue()

    def _render_generic_pdf(self, title: str, content: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1.5*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(title, styles['Heading1']),
            Spacer(1, 0.2*inch),
            Paragraph(content.replace('\n', '<br/>'), styles['Normal'])
        ]
        doc.build(elements, onFirstPage=draw_ro_template, onLaterPages=draw_ro_template)
        buffer.seek(0)
        return buffer.getvalue()

    def _paragraph_html(self, text: str, bold_vendor: str | None = None) -> str:
        cleaned = (text or "").strip()
        if not cleaned:
            return "<p class='note-paragraph'>&nbsp;</p>"
        if bold_vendor and cleaned.startswith(bold_vendor):
            remainder = cleaned[len(bold_vendor):]
            return (
                f"<p class='note-paragraph'><strong>{self._escape(bold_vendor)}</strong>"
                f"{self._escape(remainder)}</p>"
            )
        return f"<p class='note-paragraph'>{self._escape(cleaned)}</p>"

    def _build_line_items_html(self, items: list[dict]) -> str:
        rows = []
        for item in items:
            rows.append(
                f"<tr><td class='note-cell note-cell--center'>{self._escape(item.get('s_no', ''))}</td>"
                f"<td class='note-cell note-cell--center'>{self._escape(item.get('date', ''))}</td>"
                f"<td class='note-cell'>{self._escape(item.get('details', ''))}</td>"
                f"<td class='note-cell note-cell--right'>{self._escape(str(item.get('amount', '')))}</td>"
                f"<td class='note-cell'>{self._escape(item.get('rate', ''))}</td></tr>"
            )
        return "".join(rows)

    def _build_summary_rows_html(self, rows: list[dict]) -> str:
        return "".join(
            f"<tr><td class='note-cell note-cell--label'>{self._escape(str(row.get('label', '')))}</td>"
            f"<td class='note-cell'>{self._escape(str(row.get('value', '')))}</td></tr>"
            for row in rows
        )

    def _build_recommendation_html(self, paragraphs: list[str]) -> str:
        return "".join(f"<p class='note-paragraph'>{self._escape(p)}</p>" for p in paragraphs if str(p).strip())

    def _build_signature_blocks_html(self, blocks: list[dict]) -> str:
        cells = []
        for block in blocks:
            cells.append(
                f"<td class='signature-cell'>({self._escape(block.get('name_ta'))} / {self._escape(block.get('name_hi'))} / {self._escape(block.get('name_en'))})<br>"
                f"{self._escape(block.get('designation_ta'))} / {self._escape(block.get('designation_hi'))} / {self._escape(block.get('designation_en'))}</td>"
            )
        return "".join(cells)

    def _escape(self, value: str) -> str:
        return html.escape("" if value is None else str(value))
