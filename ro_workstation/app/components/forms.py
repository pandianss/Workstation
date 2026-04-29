import streamlit as st


def render_operation_form():
    with st.form("operation_form"):
        operation_type = st.selectbox(
            "Operation Type",
            ["Transfer", "Update", "Closure"],
        )

        col1, col2 = st.columns(2)

        with col1:
            branch = st.text_input("Branch Code")
            account = st.text_input("Primary Account Number")

        with col2:
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            remarks = st.text_area("Remarks")

        destination_account = ""
        update_field = ""
        update_value = ""

        if operation_type == "Transfer":
            destination_account = st.text_input("Destination Account Number")
        elif operation_type == "Update":
            update_field = st.selectbox(
                "Field To Update",
                ["branch", "holder_name", "status", "remarks"],
            )
            update_value = st.text_input("New Value")
        elif operation_type == "Closure":
            st.caption("Closure is allowed only when the account balance is zero.")

        submitted = st.form_submit_button("Validate")

        if submitted:
            return {
                "branch": branch.strip(),
                "account": account.strip(),
                "amount": float(amount),
                "type": operation_type,
                "remarks": remarks.strip(),
                "destination_account": destination_account.strip(),
                "update_field": update_field,
                "update_value": update_value.strip(),
            }

    return None
