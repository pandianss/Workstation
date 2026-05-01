from __future__ import annotations

import io
import pandas as pd
from typing import Any
from src.application.services.document_service import DocumentService
from jinja2 import Template


class MailMergeService:
    def __init__(self) -> None:
        self.doc_service = DocumentService()

    def process_merge(self, html_template: str, data_frame: pd.DataFrame) -> list[bytes]:
        """
        Merges a dataframe with an HTML template and returns a list of PDFs.
        """
        results = []
        template = Template(html_template)
        
        for _, row in data_frame.iterrows():
            # Convert row to dict for Jinja
            context = row.to_dict()
            rendered_html = template.render(**context)
            pdf_bytes = self.doc_service.generate_pdf_from_html(rendered_html)
            results.append(pdf_bytes)
            
        return results
