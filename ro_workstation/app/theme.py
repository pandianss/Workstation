import streamlit as st
from modules.utils.paths import project_path


def apply_theme():
    with open(project_path("app", "assets", "styles.css"), encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
