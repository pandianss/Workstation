from __future__ import annotations

import streamlit as st

from src.application.services.session_service import SessionService
from src.core.config.config_loader import get_app_settings
from src.core.security.auth import resolve_current_user
from src.interface.streamlit.router import PAGE_REGISTRY, render_page
from src.interface.streamlit.state import ensure_app_state, ensure_filter_state, ensure_user_state
from src.interface.streamlit.theme import apply_theme


# Base64 encoded icons from provided SVG files (White Optimized)
FAVICON_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNDQwIDE0NDAiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNNzIwIDIyTDM4NyAzNTZsNDIgNDEgMjkxLTI5MSAyOTIgMjkyIDQxLTQyek03MjAgMTQ3bC0yMSAyMS0yNTAgMjUwIDQyIDQxIDIyOS0yMjkgMjI5IDIyOSA0Mi00MnpNNzIwIDI3MmwtMjEgMjEtMTg3IDE4NyA0MiA0MiAxNjYtMTY3IDE2NyAxNjcgNDItNDJ6TTM2NiAzNzZsLTIxIDIxLTMxMiAzMTMgNDEgNDEgMjkyLTI5MSAyOTIgMjkxIDQxLTQxek0xMDc0IDM3NmwtMjEgMjEtMzEyIDMxMyA0MiA0MSAyOTEtMjkxIDI5MiAyOTEgNDItNDJ6TTM2NiA1MDFsLTIxIDIxLTI1MCAyNTAgNDIgNDIgMjI5LTIyOSAyMjkgMjI5IDQyLTQyek0xMDc0IDUwMWwtMjcxIDI3MSA0MiA0MiAyMjktMjI5IDIyOSAyMjkgNDItNDJ6TTM2NiA2MjZsLTIxIDIxLTE4NyAxODcgNDEgNDIgMTY3LTE2NyAxNjYgMTY3IDQyLTQyek0xMDc0IDYyNmwtMjEgMjEtMTg3IDE4NyA0MiA0MiAxNjYtMTY3IDE2NyAxNjcgNDEtNDJ6bS0xMDYyIDEwNGMwIDI4IDAgNTYgMCA4M0wzNjYgMTE2OGwzMzktMzM5di04NGwtMjcgMjctMzEyIDMxMi0xMDQtMTA0TDU0IDc3MnptMTQxNiAwbC0yMjkgMjI5aDBsLTEyNSAxMjUtMTI1LTEyNS0xODctMTg3LTI3LTI3djgzbDMzOSAzMzkgMzU0LTM1NHptLTE0MTYgMTI1djgzbDM1NCAzNTQgMzM5LTMzOVY4NzBMMzY2IDEyMDl6bTE0MTYgMEwxMDc0IDEyMDlsLTMzOS0zMzl2ODNsMzM5IDMzOSAzNTQtMzU0em0tMTQxNiAxMjV2ODNsMzU0IDM1NCAzMzktMzM5di04M2wtMzM5IDMzOXptMTQxNiAwTDEwNzQgMTMzNGwtMzM5LTMzOXY4M2wzMzkgMzM5IDM1NC0zNTR6Ii8+PC9zdmc+"
LOGO_B64 = FAVICON_B64

def _render_header() -> None:
    st.markdown(
        f"""
        <section class="app-hero">
            <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                <div>
                    <div class="app-hero__eyebrow">Regional operations cockpit</div>
                    <h1>{get_app_settings().app_title}</h1>
                    <p class="app-hero__subtitle">
                        Modular regional office workstation designed for the Dindigul administrative hierarchy.
                    </p>
                </div>
                <div style="padding: 5px;">
                    <img src="data:image/svg+xml;base64,{LOGO_B64}" width="50">
                </div>
            </div>
            <div class="app-badges">
                <span class="app-badge">User: {st.session_state.get("display_name", "User")}</span>
                <span class="app-badge">Role: {st.session_state.get("role", "USER")}</span>
                <span class="app-badge">Dept: {st.session_state.get("user_dept", "ALL")}</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> str:
    st.sidebar.markdown("### 🛠️ Workstation Hub")
    
    # Define Groups for logical organization
    navigation_structure = {
        "📊 Insights": ["Dashboard", "Business Analytics", "Campaign Management"],
        "🏗️ Operations": ["Operations & Returns", "Document Center", "Coordination Center"],
        "⚖️ Compliance": ["Returns & Compliance", "DICGC Return", "Branch Visits"],
        "📚 Resources": ["Knowledge Base", "Surveys & Feedback"],
        "🌐 Portals": ["Branch Portal", "Guest Portal"],
        "⚙️ Management": ["Admin"]
    }

    is_admin = st.session_state.get("role") == "ADMIN"
    all_allowed_labels = []
    label_to_page = {}
    
    for group, pages in navigation_structure.items():
        filtered_pages = pages if is_admin else [p for p in pages if p != "Admin"]
        for p in filtered_pages:
            icon = group.split()[0]
            label = f"{icon} {p}"
            all_allowed_labels.append(label)
            label_to_page[label] = p

    # Navigation Radio with Icons
    selected_label = st.sidebar.radio("Navigation", all_allowed_labels, label_visibility="collapsed")
    page = label_to_page[selected_label]
    
    # Admin Password Override Section
    if not is_admin:
        st.sidebar.markdown("---")
        with st.sidebar.expander("🔐 Unlock Admin Access"):
            with st.form("admin_upgrade_form"):
                admin_pass = st.text_input("Admin Password", type="password")
                if st.form_submit_button("Elevate Privileges", use_container_width=True):
                    settings = get_app_settings()
                    if admin_pass == settings.admin_password:
                        from src.application.services.session_service import SessionService
                        SessionService().start_session(getpass.getuser())
                        st.success("Admin access granted!")
                        st.rerun()
                    else:
                        st.error("Invalid password")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Session")
    st.sidebar.caption(f"Logged in as: **{st.session_state.get('display_name', st.session_state.get('username'))}**")
    
    if st.sidebar.button("Logout", use_container_width=True):
        import getpass
        from src.application.services.session_service import SessionService
        session_service = SessionService()
        session_service.end_session(st.session_state.get("username"))
        session_service.end_session(getpass.getuser())
        st.session_state.clear()
        st.rerun()

    # Role Toggle for Admins
    if st.session_state.get("original_role") == "ADMIN" or st.session_state.get("is_elevated"):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### View Mode")
        new_role = st.sidebar.toggle("Admin Mode", value=(st.session_state["role"] == "ADMIN"))
        target_role = "ADMIN" if new_role else "USER"
        
        if target_role != st.session_state["role"]:
            st.session_state["role"] = target_role
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("This interface is backed by the new layered architecture.")
    return page


def _require_login() -> bool:
    current_user = resolve_current_user()
    session_service = SessionService()
    settings = get_app_settings()

    if current_user.role != "GUEST":
        st.session_state["username"] = current_user.username
        st.session_state["role"] = current_user.role
        st.session_state["user_dept"] = current_user.dept
        st.session_state["user_depts"] = current_user.depts
        return True

    st.warning(f"PC User '{current_user.username}' not recognized. Please login as Admin.")
    with st.form("admin_login_main"):
        admin_pass = st.text_input("Admin Password", type="password")
        if st.form_submit_button("Login"):
            if admin_pass == settings.admin_password:
                session_service.start_session(current_user.username)
                st.success("Welcome, Admin.")
                st.rerun()
            else:
                st.error("Invalid password")
    return False


def run() -> None:
    settings = get_app_settings()
    favicon_uri = f"data:image/svg+xml;base64,{FAVICON_B64}"
    st.set_page_config(page_title=settings.app_title, page_icon=favicon_uri, layout="wide")
    ensure_app_state()
    ensure_filter_state()
    apply_theme()
    if not _require_login():
        st.stop()
    ensure_user_state()
    _render_header()
    page = _render_sidebar()
    render_page(page)
