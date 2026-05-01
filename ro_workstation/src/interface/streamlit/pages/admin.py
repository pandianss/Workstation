from __future__ import annotations

import streamlit as st

from src.application.services.admin_service import AdminService
from src.core.config.config_loader import get_app_settings, load_yaml_config
from src.core.logging.audit import AuditLogger
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    render_action_bar("Admin", ["User access", "Audit dashboard", "Config visibility"])
    if st.session_state.get("role") != "ADMIN":
        st.warning("Admin access required. Please enter the administrative password to continue.")
        with st.form("admin_escalation_form"):
            password = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Authenticate"):
                settings = get_app_settings()
                if password == settings.admin_password:
                    from src.application.services.session_service import SessionService
                    SessionService().start_session(st.session_state.get("username", "admin"))
                    st.session_state["role"] = "ADMIN"
                    st.success("Access granted. Refreshing...")
                    st.rerun()
                else:
                    st.error("Invalid administrative password.")
        return

    from src.application.services.master_service import MasterService
    master_service = MasterService()
    admin_service = AdminService()
    audit_logger = AuditLogger()
    tabs = st.tabs(["Users", "Units", "Staff", "Departments", "Audit", "Configuration"])

    with tabs[0]:
        render_data_table(admin_service.get_users_frame(), "User access", "users.xlsx")

    with tabs[1]:
        if "unit_update_msg" in st.session_state:
            st.success(st.session_state.pop("unit_update_msg"))
            
        units_df = master_service.get_units_frame()
        render_data_table(units_df, "Unit Registry", "units.xlsx")
        
        st.divider()
        st.markdown("### 👑 Assign Unit Authorities")
        staff_df = master_service.get_staff_frame()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            unit_codes = units_df['Code'].tolist()
            selected_unit_code = st.selectbox("Select Unit to Update", options=unit_codes, format_func=lambda x: f"{x} - {units_df[units_df['Code']==x]['Name'].iloc[0]}")
        
        # Get current values for the selected unit
        current_row = units_df[units_df['Code'] == selected_unit_code].iloc[0]
        
        # Filter staff by the SOL of the selected unit
        selected_unit_sol = selected_unit_code # In this system, Unit Code is the SOL
        filtered_staff_df = staff_df[staff_df['Branch SOL'] == selected_unit_sol]
        
        # Prepare staff options
        staff_list = filtered_staff_df.to_dict('records')
        staff_options = [None] + [s['Roll No'] for s in staff_list]
        def staff_format(x):
            if x is None: return "None Assigned"
            s = next((item for item in staff_list if item["Roll No"] == x), None)
            return f"{x} - {s['Name']}" if s else x

        with col2:
            current_head = current_row['Head']
            # If current head is not in filtered list (e.g. transferred), show it anyway but mark it
            if current_head and current_head != "None" and current_head not in [s['Roll No'] for s in staff_list]:
                staff_options.append(current_head)
            
            head_idx = staff_options.index(current_head) if current_head in staff_options else 0
            new_head = st.selectbox("Assign Unit Head", options=staff_options, index=head_idx, format_func=staff_format)
            
        with col3:
            current_second = current_row['2nd Line']
            if current_second and current_second != "None" and current_second not in [s['Roll No'] for s in staff_list]:
                staff_options.append(current_second)
                
            second_idx = staff_options.index(current_second) if current_second in staff_options else 0
            new_second = st.selectbox("Assign 2nd Line", options=staff_options, index=second_idx, format_func=staff_format)
            
        if st.button("💾 Update Unit Authorities", use_container_width=True):
            if master_service.update_unit_authorities(selected_unit_code, new_head, new_second):
                st.session_state["unit_update_msg"] = f"✅ Authorities updated successfully for Unit {selected_unit_code}"
                st.rerun()
            else:
                st.error("❌ Failed to update unit authorities.")

    with tabs[2]:
        staff_df = master_service.get_staff_frame()
        render_data_table(staff_df, "Staff Registry", "staff.xlsx")
        
        st.divider()
        st.markdown("### ✍️ Update Staff Trilingual Names")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_roll = st.text_input("Search Roll No")
        
        if search_roll:
            staff_match = staff_df[staff_df['Roll No'] == search_roll]
            if not staff_match.empty:
                s_row = staff_match.iloc[0]
                st.info(f"Staff Found: **{s_row['Name (En)']}** ({s_row['Designation']})")
                
                with st.form("staff_name_update"):
                    new_hi = st.text_input("Name (Hindi)", value=s_row['Name (Hi)'])
                    new_ta = st.text_input("Name (Tamil)", value=s_row['Name (Ta)'])
                    
                    if st.form_submit_button("Update Trilingual Names"):
                        if master_service.update_staff_names(search_roll, new_hi, new_ta):
                            st.session_state["unit_update_msg"] = f"✅ Trilingual names updated for {search_roll}"
                            st.rerun()
                        else:
                            st.error("Failed to update staff names.")
            else:
                st.warning("Staff member not found.")

    with tabs[3]:
        render_data_table(master_service.get_departments_frame(), "Department Registry", "departments.xlsx")

    with tabs[4]:
        render_data_table(audit_logger.to_frame(), "Audit trail", "audit_log.xlsx")

    with tabs[5]:
        st.json(get_app_settings().model_dump())
        st.divider()
        st.markdown("### Advances Scheme Mapping (3-Level)")
        scheme_path = "data/scheme_config.json"
        import json
        import os
        if os.path.exists(scheme_path):
            with open(scheme_path, 'r') as f:
                schemes = json.load(f)
            
            new_schemes_str = st.text_area("Edit Scheme Mapping (JSON)", value=json.dumps(schemes, indent=2), height=300)
            if st.button("Update Scheme Mapping"):
                try:
                    json.loads(new_schemes_str)
                    with open(scheme_path, 'w') as f:
                        f.write(new_schemes_str)
                    st.success("Scheme mapping updated successfully.")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
        
        st.markdown("### Role Map")
        st.json(load_yaml_config("roles.yaml"))
