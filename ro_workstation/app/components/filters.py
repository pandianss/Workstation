import streamlit as st

def render_task_filters():
    col1, col2, col3 = st.columns(3)

    with col1:
        status = st.selectbox(
            "Status",
            ["All", "OPEN", "CLOSED"]
        )

    with col2:
        priority = st.selectbox(
            "Priority",
            ["All", "P1", "P2", "P3", "P4"] # Aligning with backend VALID_PRIORITIES
        )

    with col3:
        search = st.text_input("Search")

    return {
        "status": status,
        "priority": priority,
        "search": search
    }
