from __future__ import annotations

import streamlit as st

from src.application.services.operation_service import OperationService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_filter_panel


def render() -> None:
    service = OperationService()
    render_action_bar("Operations", ["Validated workflow", "Audit log", "Account exports"])
    render_filter_panel("Controlled execution", "Submit operational changes through one validated workflow.")

    with st.form("operation_form_v2"):
        op_type = st.selectbox("Operation Type", ["Transfer", "Update", "Closure"])
        col1, col2 = st.columns(2)
        with col1:
            unit = st.text_input("Unit Code")
            account = st.text_input("Primary Account Number")
            destination_account = st.text_input("Destination Account Number") if op_type == "Transfer" else ""
        with col2:
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            remarks = st.text_area("Remarks")
            update_field = st.selectbox("Field To Update", ["unit", "holder_name", "status", "remarks"]) if op_type == "Update" else ""
            update_value = st.text_input("New Value") if op_type == "Update" else ""
        submitted = st.form_submit_button("Validate and Submit")

    if submitted:
        result = service.process_operation(
            {
                "unit": unit.strip(),
                "account": account.strip(),
                "amount": float(amount),
                "type": op_type,
                "remarks": remarks.strip(),
                "destination_account": destination_account.strip(),
                "update_field": update_field,
                "update_value": update_value.strip(),
            },
            user=st.session_state.get("username", "system"),
        )
        if result["success"]:
            st.success(result["message"])
            if result.get("details"):
                st.json(result["details"])
        else:
            st.error(result["message"])

    accounts = service.get_accounts()
    operations = service.get_operation_history(limit=50)
    tabs = st.tabs(["Accounts", "Operation History"])
    with tabs[0]:
        render_data_table(accounts, "Accounts", "accounts.xlsx")
    with tabs[1]:
        render_data_table(operations, "Operation History", "operation_history.xlsx")
