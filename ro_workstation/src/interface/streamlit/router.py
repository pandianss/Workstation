from __future__ import annotations

from importlib import import_module


PAGE_REGISTRY = {
    "Dashboard": "src.interface.streamlit.pages.dashboard",
    "Analytics": "src.interface.streamlit.pages.mis",
    "Knowledge Hub": "src.interface.streamlit.pages.knowledge_hub",
    "Operations": "src.interface.streamlit.pages.operations",
    "Document Center": "src.interface.streamlit.pages.intelligence",
    "Admin": "src.interface.streamlit.pages.admin",
}


def render_page(page_name: str) -> None:
    module = import_module(PAGE_REGISTRY[page_name])
    module.render()
