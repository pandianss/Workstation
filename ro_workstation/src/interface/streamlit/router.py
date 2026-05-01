from __future__ import annotations

from importlib import import_module


PAGE_REGISTRY = {
    "Dashboard": "src.interface.streamlit.pages.dashboard",
    "Business Analytics": "src.interface.streamlit.pages.mis",
    "Policy & Product Archive": "src.interface.streamlit.pages.knowledge",
    "Document Center": "src.interface.streamlit.pages.execution",
    "Surveys": "src.interface.streamlit.pages.surveys",
    "Statutory Returns": "src.interface.streamlit.pages.returns",
    "Admin": "src.interface.streamlit.pages.admin",
}


def render_page(page_name: str) -> None:
    module = import_module(PAGE_REGISTRY[page_name])
    module.render()
