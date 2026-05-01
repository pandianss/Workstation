from __future__ import annotations

import streamlit as st

from src.application.services.admin_service import AdminService
from src.core.config.config_loader import get_app_settings, load_yaml_config
from src.core.logging.audit import AuditLogger
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    render_action_bar("Admin", ["User access", "Audit dashboard", "Config visibility"])
    if st.session_state.get("role") != "ADMIN":
        st.warning("Admin access required.")
        return

    from src.application.services.master_service import MasterService
    master_service = MasterService()
    admin_service = AdminService()
    audit_logger = AuditLogger()
    tabs = st.tabs(["Users", "Branches", "Staff", "Departments", "Audit", "Configuration"])

    with tabs[0]:
        render_data_table(admin_service.get_users_frame(), "User access", "users.xlsx")

    with tabs[1]:
        render_data_table(master_service.get_branches_frame(), "Branch Registry", "branches.xlsx")

    with tabs[2]:
        render_data_table(master_service.get_staff_frame(), "Staff Registry", "staff.xlsx")

    with tabs[3]:
        render_data_table(master_service.get_departments_frame(), "Department Registry", "departments.xlsx")

    with tabs[4]:
        render_data_table(audit_logger.to_frame(), "Audit trail", "audit_log.xlsx")

    with tabs[5]:
        st.json(get_app_settings().model_dump())
        st.markdown("### Role Map")
        st.json(load_yaml_config("roles.yaml"))
