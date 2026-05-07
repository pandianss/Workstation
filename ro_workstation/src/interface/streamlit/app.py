from __future__ import annotations

import streamlit as st
import datetime

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
    display_name = st.session_state.get("display_name", "User")
    st.markdown(
        f"""
        <div class="top-bar-container">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.4rem;">👋</span>
                <span style="font-size: 1.1rem; font-weight: 600; color: #ffffff; letter-spacing: 0.5px;">
                    Welcome, {display_name.upper()} 
                    <span style="color: rgba(255,255,255,0.4); margin: 0 12px; font-weight: 300;">|</span> 
                    <span style="color: rgba(255,255,255,0.7); font-weight: 400; font-size: 0.95rem;">Regional Operations Cockpit</span>
                </span>
            </div>
            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5); font-weight: 500;">
                {datetime.datetime.now().strftime("%A, %d %B %Y")}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _render_sidebar() -> str:
    from src.core.logging.audit import AuditLogger
    audit_logger = AuditLogger()
    username = st.session_state.get("username", "GUEST")
    
    st.sidebar.markdown("### 🚀 Quick Access")
    frequent_pages = audit_logger.get_frequent_pages(username)
    
    # We use a session state key to handle clicks from quick access
    if "requested_page" not in st.session_state:
        st.session_state["requested_page"] = "Dashboard"

    # Robust CSS for Link-style Navigation
    st.sidebar.markdown(
        """
        <style>
        /* Target buttons in the sidebar to look like links and be left-aligned */
        [data-testid="stSidebar"] .stButton > button {
            background-color: transparent !important;
            border: none !important;
            padding: 0px !important;
            margin: 0px !important;
            height: 24px !important;
            min-height: 24px !important;
            line-height: 24px !important;
            color: rgba(255, 255, 255, 0.7) !important;
            text-align: left !important;
            justify-content: flex-start !important;
            font-size: 0.95rem !important;
            font-weight: 400 !important;
            box-shadow: none !important;
            display: flex !important;
        }
        /* Ensure the internal flex container also aligns left */
        [data-testid="stSidebar"] .stButton > button div {
            justify-content: flex-start !important;
            text-align: left !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            color: #ffffff !important;
            background-color: transparent !important;
            text-decoration: underline !important;
        }
        /* Tighten spacing between elements in sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if frequent_pages:
        for p in frequent_pages:
            if st.sidebar.button(f"👉 {p}", key=f"quick_{p}", use_container_width=True):
                st.session_state["requested_page"] = p
                st.rerun()
    else:
        st.sidebar.caption("No frequent pages yet.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Workstation Hub")
    
    # Define Groups for logical organization
    navigation_structure = {
        "📊 Insights": ["Dashboard", "Business Analytics", "Campaign Management"],
        "🏗️ Operations": ["Operations & Returns", "Letter Generator", "Document Center", "Coordination Center"],
        "⚖️ Compliance": ["Returns & Compliance", "DICGC Return", "Branch Visits"],
        "📚 Resources": ["Knowledge Base", "Surveys & Feedback"],
        "🌐 Portals": ["Branch Portal", "Guest Portal"],
        "⚙️ Management": ["Admin"]
    }

    is_admin = st.session_state.get("role") == "ADMIN"
    current_page = st.session_state.get("requested_page", "Dashboard")

    # Grouped Navigation with Expanders
    for group, pages in navigation_structure.items():
        # Check if any page in this group is allowed
        allowed_in_group = [p for p in pages if is_admin or p != "Admin"]
        if not allowed_in_group:
            continue
            
        with st.sidebar.expander(group, expanded=(current_page in allowed_in_group)):
            for p in allowed_in_group:
                # Use primary button style for the active page
                btn_type = "primary" if p == current_page else "secondary"
                if st.button(p, key=f"nav_btn_{p}", use_container_width=True, type=btn_type):
                    if p != current_page:
                        st.session_state["requested_page"] = p
                        audit_logger.log(username, f"Viewed page {p}")
                        st.rerun()

    page = st.session_state["requested_page"]
    
    # Log initial view if not already logged for this session's first run
    if "first_view_logged" not in st.session_state:
        audit_logger.log(username, f"Viewed page {page}")
        st.session_state["first_view_logged"] = True
    
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
