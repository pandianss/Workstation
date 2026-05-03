from __future__ import annotations
import streamlit as st
from src.core.config.config_loader import get_app_settings
from src.interface.streamlit.pages import guest_portal
from src.interface.streamlit.theme import apply_theme

def run():
    settings = get_app_settings()
    st.set_page_config(page_title="Public Business Portal | Dindigul Region", layout="wide")
    apply_theme()
    guest_portal.render()

if __name__ == "__main__":
    run()
