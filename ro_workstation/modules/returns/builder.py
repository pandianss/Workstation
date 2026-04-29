import streamlit as st

def render_return_form(return_name: str, fields: list):
    st.write(f"### {return_name}")
    form_data = {}
    with st.form(f"return_{return_name}"):
        for field in fields:
            form_data[field] = st.text_input(field)
        
        if st.form_submit_button("Submit Return"):
            st.success(f"{return_name} submitted successfully!")
            return form_data
    return None
