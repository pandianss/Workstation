import streamlit as st


def render_preview(data):
    st.markdown("### Confirm Details")
    st.markdown(
        """
        <div class="preview-shell">
            <div class="section-kicker">Review the request carefully before it is written to the operation log.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preview_fields = {
        "Operation": data.get("type", "-"),
        "Branch": data.get("branch", "-"),
        "Primary Account": data.get("account", "-"),
        "Amount": f"{data.get('amount', 0):,.2f}",
        "Remarks": data.get("remarks", "-") or "-",
    }

    if data.get("destination_account"):
        preview_fields["Destination Account"] = data["destination_account"]
    if data.get("update_field"):
        preview_fields["Field To Update"] = data["update_field"]
    if data.get("update_value"):
        preview_fields["New Value"] = data["update_value"]

    preview_html = "".join(
        f'<div class="preview-item"><strong>{label}</strong>{value}</div>'
        for label, value in preview_fields.items()
    )
    st.markdown(f'<div class="preview-list">{preview_html}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        confirm = st.button("Confirm & Submit")

    with col2:
        cancel = st.button("Cancel", type="secondary")

    if cancel:
        st.warning("Operation cancelled.")
        return False

    return confirm
