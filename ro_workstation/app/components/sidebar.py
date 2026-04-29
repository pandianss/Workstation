import streamlit as st
from app.services.task_service import get_task_summary

def render_sidebar():
    # Logo is optional, we'll gracefully handle it if it doesn't exist
    try:
        st.sidebar.image("app/assets/logo.svg", width=120)
    except:
        pass
        
    st.sidebar.markdown("### RO Workstation")

    summary = get_task_summary()

    st.sidebar.markdown("#### Status")
    st.sidebar.metric("Open Tasks", summary["open"])
    st.sidebar.metric("Overdue", summary["overdue"])

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Operations", "Intelligence", "Performance MIS", "Admin"]
    )

    return page
