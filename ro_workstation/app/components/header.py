import streamlit as st
from datetime import datetime


def render_header():
    user_name = st.session_state.get("username", "RO Manager")
    user_dept = st.session_state.get("user_dept", "ALL")
    today_label = datetime.now().strftime("%d %b %Y")

    st.markdown(
        f"""
        <section class="app-hero">
            <div class="app-hero__eyebrow">Regional operations cockpit</div>
            <h1>Regional Office Control Center</h1>
            <p class="app-hero__subtitle">
                A cleaner command surface for operations, intelligence, and performance oversight.
                Designed to keep high-priority work visible and routine actions easy to execute.
            </p>
            <div class="app-badges">
                <span class="app-badge">User: {user_name}</span>
                <span class="app-badge">Department: {user_dept}</span>
                <span class="app-badge">Snapshot: {today_label}</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
