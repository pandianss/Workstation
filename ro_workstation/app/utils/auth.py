import getpass
import streamlit as st
from app.services.admin_service import get_users
from app.services.config_service import get_value


from app.services.session_service import is_session_active, start_session, end_session

def require_login():
    pc_username = getpass.getuser()
    
    # 1. Persistent Session Check (Cross-Reload)
    is_admin_override = is_session_active(pc_username)
    
    if is_admin_override:
        st.session_state["admin_logged_in"] = True
        st.session_state["username"] = "special_admin"
        st.session_state["role"] = "ADMIN"
        st.session_state["user_dept"] = "ALL"
        st.sidebar.success("🛡️ RO Admin Access Active")
        if st.sidebar.button("Exit Admin Mode"):
            end_session(pc_username)
            st.session_state["admin_logged_in"] = False
            st.rerun()
        return True

    # 2. Standard Staff Auto-Login
    users_df = get_users()
    user_record = users_df[users_df["username"] == pc_username]

    if not user_record.empty:
        role = user_record.iloc[0].get("role", "USER")
        depts = user_record.iloc[0].get("depts", [user_record.iloc[0].get("dept", "3933")])
        
        st.session_state["username"] = pc_username
        st.session_state["role"] = role
        st.session_state["user_depts"] = depts
        st.sidebar.success(f"👤 {pc_username} ({role})")

        with st.sidebar.expander("Admin Override"):
            with st.form("admin_login"):
                admin_pass = st.text_input("Admin Password", type="password")
                if st.form_submit_button("Login"):
                    expected_pass = get_value("admin_password", "admin")
                    if admin_pass == expected_pass:
                        start_session(pc_username) # Persist across reloads
                        st.session_state["admin_logged_in"] = True
                        st.rerun()
                    else:
                        st.error("Invalid password")
        return True

    # 3. Fallback for unrecognized PC users
    st.warning(f"PC User '{pc_username}' not recognized. Please login as Admin.")
    with st.form("admin_login_main"):
        admin_pass = st.text_input("Admin Password", type="password")
        if st.form_submit_button("Login"):
            expected_pass = get_value("admin_password", "admin")
            if admin_pass == expected_pass:
                start_session(pc_username)
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid password")
    return False
