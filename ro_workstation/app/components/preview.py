import streamlit as st

def render_preview(data):
    st.markdown("### Confirm Details")

    st.json(data)

    col1, col2 = st.columns(2)

    with col1:
        confirm = st.button("Confirm & Submit")

    with col2:
        cancel = st.button("Cancel")

    if cancel:
        st.warning("Operation cancelled.")
        return False

    return confirm
