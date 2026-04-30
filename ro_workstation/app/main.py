import streamlit as st
from app.components.sidebar import render_sidebar
from app.components.header import render_header
from app.views.dashboard import render_dashboard
from app.views.operations import render_operations
from app.views.intelligence import render_intelligence
from app.utils.auth import require_login
from app.theme import apply_theme

st.set_page_config(
    page_title="RO Workstation",
    page_icon=":bank:",
    layout="wide",
)

apply_theme()

if not require_login():
    st.stop()

render_header()
page = render_sidebar()

if page == "Dashboard":
    render_dashboard()
elif page == "Operations":
    render_operations()
elif page == "Guardian":
    from app.views.guardian import render_guardian_view
    render_guardian_view()
elif page == "Intelligence":
    render_intelligence()
elif page == "Performance MIS":
    from app.views.mis import render_mis_dashboard

    render_mis_dashboard()
elif page == "Admin":
    from app.views.admin import render_admin

    render_admin()
