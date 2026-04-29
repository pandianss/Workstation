import streamlit as st


def render_header():
    col1, col2 = st.columns([6, 2])

    with col1:
        st.title("Regional Office Control Center")

    with col2:
        user_name = st.session_state.get("username", "RO Manager")
        user_dept = st.session_state.get("user_dept", "ALL")

        st.markdown(f"**User:** {user_name}")
        st.markdown(f"**Dept:** {user_dept}")
