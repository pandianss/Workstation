import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st
from .paths import project_path

def get_authenticator():
    with project_path("config", "users.yaml").open(encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator, config

def require_login():
    authenticator, config = get_authenticator()
    
    # Render login widget
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)
        
    auth_status = st.session_state.get("authentication_status")

    if auth_status:
        # Logged in
        # Set user details in session state for easy access
        username = st.session_state.get("username")
        user_config = config['credentials']['usernames'].get(username, {})
        st.session_state["user_role"] = user_config.get('role', '')
        st.session_state["user_dept"] = user_config.get('department', 'ALL')
        st.session_state["user_name"] = user_config.get('name', username or 'User')
        
        # Add a logout button to sidebar
        with st.sidebar:
            st.write(f"Welcome, {st.session_state['user_name']} ({st.session_state['user_dept']})")
            authenticator.logout('Logout', 'sidebar')
        return True
    elif auth_status is False:
        st.error('Username/password is incorrect')
        return False
    elif auth_status is None:
        st.warning('Please enter your username and password')
        return False
