import streamlit as st
from app.components.forms import render_operation_form
from app.components.preview import render_preview
from app.services.operation_service import (
    process_operation,
    get_accounts,
    get_operation_history,
)


def render_operations():
    st.markdown("## Operations")
    st.markdown(
        """
        <div class="glass-panel">
            <div class="section-title"><strong>Controlled execution</strong></div>
            <div class="section-kicker">
                Validate changes before submission, keep account context nearby, and make audit-friendly updates with less friction.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    execute_tab, accounts_tab, history_tab = st.tabs(
        ["Execute Operation", "Accounts", "Operation History"]
    )

    with execute_tab:
        form_data = render_operation_form()

        if form_data:
            confirmed = render_preview(form_data)

            if confirmed:
                result = process_operation(
                    form_data,
                    user=st.session_state.get("username", "system"),
                )

                if result["success"]:
                    st.success(result["message"])
                    st.caption(f"Operation ID: {result['operation_id']}")
                    if result.get("details"):
                        st.json(result["details"])
                else:
                    st.error(result["message"])

    with accounts_tab:
        st.caption("These accounts are the live operation targets used by the workstation.")
        st.dataframe(get_accounts(), use_container_width=True, hide_index=True)

    with history_tab:
        st.caption("Each submitted operation is recorded here, including failed attempts.")
        st.dataframe(get_operation_history(), use_container_width=True, hide_index=True)

    with history_tab:
        st.caption("Each submitted operation is recorded here, including failed attempts.")
        st.dataframe(get_operation_history(), use_container_width=True, hide_index=True)
