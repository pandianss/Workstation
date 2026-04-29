import streamlit as st

def get_user_role():
    return st.session_state.get("role", "USER")

def require_role(allowed_roles):
    role = get_user_role()
    return role in allowed_roles
