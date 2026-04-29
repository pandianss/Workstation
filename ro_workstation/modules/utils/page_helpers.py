from datetime import date

import streamlit as st
from ..ui.theme import render_hero


DEPARTMENT_OPTIONS = ["ALL", "FI", "CRMD", "PLAN", "ARID", "HRDD", "GAD", "COM", "MKT", "LAW", "INS", "RSK", "SME", "RET", "RCC"]


def current_user() -> dict:
    return {
        "username": st.session_state.get("username", "admin"),
        "name": st.session_state.get("user_name", "User"),
        "role": st.session_state.get("user_role", "RO_User"),
        "department": st.session_state.get("user_dept", "ALL"),
    }


def render_page_header(title: str, description: str | None = None, allowed_departments: list[str] | None = None) -> dict:
    user = current_user()
    render_hero(
        title,
        description or "",
        chips=[
            f"User: {user['name']}",
            f"Role: {user['role']}",
            f"Department: {user['department']}",
        ],
    )
    if allowed_departments and user["department"] not in {"ALL", *allowed_departments}:
        st.warning(
            f"This page is tuned for {', '.join(allowed_departments)} users. "
            "You can still review it, but outputs may need department validation."
        )
    return user


def render_generation_result(label: str, content: str, download_name: str) -> None:
    st.markdown(f"### {label}")
    st.text_area(label, value=content, height=320)
    st.download_button(
        f"Download {label}",
        data=content,
        file_name=download_name,
        mime="text/plain",
    )


def format_due_date(value) -> str:
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return "No due date"
    return str(value)
