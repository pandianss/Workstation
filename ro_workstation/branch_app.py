from __future__ import annotations
import streamlit as st
from src.core.config.config_loader import get_app_settings
from src.interface.streamlit.pages import branch_portal
from src.interface.streamlit.theme import apply_theme

def run():
    settings = get_app_settings()
    st.set_page_config(page_title="Branch Connect | Dindigul Region", layout="wide")
    apply_theme()
    
    # Simple login simulation for branch
    if "branch_authenticated" not in st.session_state:
        st.markdown("### 🏦 Branch Portal Login")
        with st.form("branch_login"):
            sol = st.text_input("Enter Branch SOL ID", placeholder="e.g. 3933")
            if st.form_submit_button("Access Portal"):
                if sol:
                    st.session_state["branch_authenticated"] = True
                    st.session_state["sol"] = sol
                    st.rerun()
    else:
        branch_portal.render()

if __name__ == "__main__":
    run()
