import getpass
import streamlit as st
from app.services.admin_service import get_users
from app.services.config_service import get_value


def require_login():
    pc_username = getpass.getuser()

    if st.session_state.get("admin_logged_in"):
        st.session_state["username"] = "special_admin"
        st.session_state["role"] = "ADMIN"
        st.session_state["user_dept"] = "ALL"
        st.sidebar.success("Logged in as Special Admin")
        if st.sidebar.button("Logout Admin"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
        return True

    users_df = get_users()
    user_record = users_df[users_df["username"] == pc_username]

    if not user_record.empty:
        role = user_record.iloc[0]["role"]
        dept = user_record.iloc[0]["dept"] if "dept" in user_record.columns else "ALL"
        st.session_state["username"] = pc_username
        st.session_state["role"] = role
        st.session_state["user_dept"] = dept or "ALL"
        st.sidebar.success(f"Auto-logged in as {pc_username} ({role})")

        with st.sidebar.expander("Admin Override"):
            with st.form("admin_login"):
                admin_pass = st.text_input("Admin Password", type="password")
                if st.form_submit_button("Login"):
                    expected_pass = get_value("admin_password", "admin")
                    if admin_pass == expected_pass:
                        st.session_state["admin_logged_in"] = True
                        st.session_state["role"] = "ADMIN"
                        st.session_state["username"] = "special_admin"
                        st.session_state["user_dept"] = "ALL"
                        st.rerun()
                    else:
                        st.error("Invalid password")
        return True

    st.warning(f"PC User '{pc_username}' not recognized. Please login as Admin to continue.")
    with st.form("admin_login_main"):
        admin_pass = st.text_input("Admin Password", type="password")
        if st.form_submit_button("Login"):
            expected_pass = get_value("admin_password", "admin")
            if admin_pass == expected_pass:
                st.session_state["admin_logged_in"] = True
                st.session_state["role"] = "ADMIN"
                st.session_state["username"] = "special_admin"
                st.session_state["user_dept"] = "ALL"
                st.rerun()
            else:
                st.error("Invalid password")
    return False
