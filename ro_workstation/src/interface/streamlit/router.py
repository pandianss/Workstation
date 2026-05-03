from __future__ import annotations

from importlib import import_module


PAGE_REGISTRY = {
    "Dashboard": "src.interface.streamlit.pages.dashboard",
    "Operations & Returns": "src.interface.streamlit.pages.operational_wizards",
    "Document Center": "src.interface.streamlit.pages.execution",
    "Business Analytics": "src.interface.streamlit.pages.mis",
    "Returns & Compliance": "src.interface.streamlit.pages.returns",
    "Coordination Center": "src.interface.streamlit.pages.coordination",
    "DICGC Return": "src.interface.streamlit.pages.dicgc",
    "Knowledge Base": "src.interface.streamlit.pages.knowledge",
    "Branch Visits": "src.interface.streamlit.pages.visits",
    "Surveys & Feedback": "src.interface.streamlit.pages.surveys",
    "Admin": "src.interface.streamlit.pages.admin",
    "Branch Portal": "src.interface.streamlit.pages.branch_portal",
    "Guest Portal": "src.interface.streamlit.pages.guest_portal",
}


def render_page(page_name: str) -> None:
    module = import_module(PAGE_REGISTRY[page_name])
    module.render()
