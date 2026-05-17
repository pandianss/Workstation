from __future__ import annotations

import streamlit as st
import datetime
import os
import pandas as pd
from src.core.paths import project_path

from src.application.services.admin_service import AdminService
from src.core.config.config_loader import get_app_settings, load_yaml_config
from src.core.logging.audit import AuditLogger
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_premium_metrics


def render_upload_card(title: str, expected_name: str, description: str, category: str, service) -> None:
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(description)
        st.code(f"Expected: {expected_name}", language="text")
        
        uploaded_file = st.file_uploader(f"Upload {title}", type=["csv", "xlsx"], key=f"up_{category}", label_visibility="collapsed")
        
        if uploaded_file:
            if st.button(f"Confirm {title} Update", key=f"btn_{category}", use_container_width=True, type="primary"):
                with st.spinner(f"Updating {category}..."):
                    success = service.update_master_file(category, uploaded_file.getvalue(), uploaded_file.name)
                    if success:
                        st.success(f"✅ {title} updated successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to update {title}. Please check the file format.")


def render() -> None:
    render_action_bar("Admin", ["User access", "Audit dashboard", "Config visibility"])
    
    # Enforce administrative password escalation
    if not st.session_state.get("admin_unlocked"):
        st.warning("⚠️ Administrative Lock: Please enter the regional master password to unlock secure settings.")
        with st.form("admin_escalation_form"):
            password = st.text_input("Master Admin Password", type="password")
            if st.form_submit_button("🔓 Unlock Admin Hub"):
                settings = get_app_settings()
                if password == settings.admin_password:
                    from src.application.services.session_service import SessionService
                    SessionService().start_session(st.session_state.get("username", "admin"))
                    st.session_state["admin_unlocked"] = True
                    st.success("Admin Hub Unlocked! Refreshing...")
                    st.rerun()
                else:
                    st.error("Invalid administrative password.")
        return

    from src.application.services.master_service import MasterService
    
    # Cache the service instance to avoid multiple DB connections/instantiations
    @st.cache_resource
    def get_services():
        return MasterService(), AdminService()
    
    master_service, admin_service = get_services()
    audit_logger = AuditLogger()
    
    # Cache the dataframes to improve UI responsiveness
    @st.cache_data(ttl=600) # 10 minute cache
    def load_cached_frames():
        return master_service.get_units_frame(), master_service.get_staff_frame(), master_service.get_departments_frame()

    tabs = st.tabs(["👥 Users", "🏦 Units", "👨‍💼 Staff", "🏢 Departments", "📁 Upload Masters", "📜 Audit", "⚙️ Configuration"])

    with tabs[0]:
        render_data_table(admin_service.get_users_frame(), "User access", "users.xlsx")

    with tabs[1]:
        if "unit_update_msg" in st.session_state:
            st.success(st.session_state.pop("unit_update_msg"))
            
        units_df, staff_df, depts_df = load_cached_frames()
        render_data_table(units_df, "Unit Registry", "units.xlsx")
        
        st.divider()
        st.markdown("### 👑 Assign Unit Authorities")
        
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1])
        with col1:
            unit_codes = sorted(units_df['Code'].tolist())
            selected_unit_code = st.selectbox("Select Unit to Update", options=unit_codes, format_func=lambda x: f"{x} - {units_df[units_df['Code']==x]['Name'].iloc[0]}")
        
        current_row = units_df[units_df['Code'] == selected_unit_code].iloc[0]
        selected_unit_sol = selected_unit_code 
        filtered_staff_df = staff_df[staff_df['Branch SOL'] == selected_unit_sol]
        staff_list = filtered_staff_df.to_dict('records')
        staff_options = [None] + [s['Roll No'] for s in staff_list]
        def staff_format(x):
            if x is None: return "None Assigned"
            s = next((item for item in staff_list if item["Roll No"] == x), None)
            return f"{x} - {s['Name (En)']}" if s else x

        with col2:
            current_head = current_row['Head']
            if current_head and current_head != "None" and current_head not in [s['Roll No'] for s in staff_list]:
                staff_options.append(current_head)
            head_idx = staff_options.index(current_head) if current_head in staff_options else 0
            new_head = st.selectbox("Assign Unit Head", options=staff_options, index=head_idx, format_func=staff_format)
            
        with col3:
            current_second = current_row['2nd Line']
            # Exclude the newly selected head from the 2nd line options
            second_options = [opt for opt in staff_options if opt != new_head or opt is None]
            
            if current_second and current_second != "None" and current_second not in [s['Roll No'] for s in staff_list]:
                if current_second not in second_options:
                    second_options.append(current_second)
            
            second_idx = second_options.index(current_second) if current_second in second_options else 0
            new_second = st.selectbox("Assign 2nd Line", options=second_options, index=second_idx, format_func=staff_format)
        
        with col4:
            eff_date_val = st.date_input("Effective From", value=datetime.date.today())
            eff_date = eff_date_val.strftime("%d.%m.%Y")
            
        if st.button("💾 Update Unit Authorities", use_container_width=True):
            with st.spinner("Updating Unit Authorities..."):
                if master_service.update_unit_authorities(selected_unit_code, new_head, new_second, eff_date):
                    st.cache_data.clear()
                    st.session_state["unit_update_msg"] = f"✅ Authorities updated successfully for Unit {selected_unit_code}"
                    st.rerun()

    with tabs[2]:
        st.markdown("### 👨‍💼 Regional Staff Registry")
        units_df, staff_df, depts_df = load_cached_frames()
        render_data_table(staff_df, "Staff Registry", "staff.xlsx")
        
        # --- Staff Details Section ---
        st.divider()
        st.markdown("### ✍️ Update Staff Details (with History)")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            search_roll = st.text_input("Search Roll No", key="staff_search_roll")
        
        if search_roll:
            staff_match = staff_df[staff_df['Roll No'] == search_roll]
            if not staff_match.empty:
                s_row = staff_match.iloc[0]
                st.info(f"Staff Found: **{s_row['Name (En)']}** (Current: {s_row['Designation']} at SOL {s_row['Branch SOL']})")
                
                with st.form("staff_details_update"):
                    f1, f2, f3 = st.columns(3)
                    with f1:
                        new_hi = st.text_input("Name (Hindi)", value=s_row['Name (Hi)'])
                        new_ta = st.text_input("Name (Tamil)", value=s_row['Name (Ta)'])
                    with f2:
                        new_sol = st.text_input("SOL Code", value=s_row['Branch SOL'])
                        new_desig = st.text_input("Designation", value=s_row['Designation'])
                        new_gender = st.radio("Gender", options=["M", "F"], index=0 if s_row['Gender'] == "M" else 1, horizontal=True)
                    with f3:
                        # Parse existing dates safely
                        try:
                            def_from = datetime.datetime.strptime(s_row['Posting From'], "%Y-%m-%d").date() if s_row['Posting From'] else datetime.date.today()
                        except: def_from = datetime.date.today()
                        
                        try:
                            def_to = datetime.datetime.strptime(s_row['Posting To'], "%Y-%m-%d").date() if s_row['Posting To'] else None
                        except: def_to = None

                        new_p_from = st.date_input("Posting From", value=def_from)
                        new_p_to = st.date_input("Posting To (Optional)", value=def_to)
                    
                    # Department Allotment for RO Staff
                    dept_options = sorted(depts_df['Code'].tolist()) if not depts_df.empty else []
                    current_depts = s_row['Departments'].split(", ") if s_row['Departments'] else []
                    
                    st.markdown("🏢 **Department Allotment (RO/3933 Only)**")
                    new_depts = st.multiselect("Select Allotted Departments", 
                                             options=dept_options, 
                                             default=[d for d in current_depts if d in dept_options],
                                             help="RO staff (SOL 3933) can be assigned to multiple departments.")

                    if st.form_submit_button("💾 Save Changes & Archive History"):
                        with st.spinner("Saving Staff Changes..."):
                            # Format back to string
                            p_from_str = new_p_from.strftime("%d.%m.%Y")
                            p_to_str = new_p_to.strftime("%d.%m.%Y") if new_p_to else ""
                            
                            # 1. Update Core Details
                            detail_ok = master_service.update_staff_details(search_roll, new_hi, new_ta, new_sol, new_desig, new_gender, p_from_str, p_to_str)
                            # 2. Update Department Allotment
                            allot_ok = master_service.allot_staff_to_departments(search_roll, new_depts)
                            
                            if detail_ok and allot_ok:
                                st.cache_data.clear()
                                st.session_state["unit_update_msg"] = f"✅ Updated profile and department links for {search_roll}"
                                st.rerun()
                            else:
                                st.error("Failed to update staff record.")
                
                # Show History if exists
                meta = next((r.metadata for r in master_service.repo.get_by_category("STAFF") if r.code == search_roll), {})
                if meta.get("postings"):
                    with st.expander("🕒 View Posting History"):
                        st.table(pd.DataFrame(meta["postings"]))
            else:
                st.warning("Staff member not found.")

    with tabs[3]:
        units_df, staff_df, depts_df = load_cached_frames()
        render_data_table(depts_df, "Department Registry", "departments.xlsx")

    with tabs[4]:
        st.markdown("### 📁 Regional Master Registry")
        st.caption("Securely update staff, branch, and department masters using the file uploaders below.")
        
        staff_records = master_service.get_by_category("STAFF")
        unit_records = master_service.get_by_category("UNIT")
        dept_records = master_service.get_by_category("DEPT")
        metrics = {
            "Staff Records": len(staff_records),
            "Active Units": len([r for r in unit_records if r.is_active]),
            "Departments": len(dept_records),
            "Last Sync": datetime.datetime.now().strftime("%H:%M")
        }
        render_premium_metrics(metrics)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            render_upload_card(
                "Staff Registry", 
                "Staff.csv", 
                "Update employee records, designations, and postings.",
                "STAFF",
                master_service
            )
            
            render_upload_card(
                "Budget Targets", 
                "Budget3.csv", 
                "Update annual business targets for all parameters.",
                "BUDGET",
                master_service
            )

        with col_u2:
            render_upload_card(
                "Branch Master", 
                "branches.csv", 
                "Update branch addresses, types, and SOL mappings.",
                "UNIT",
                master_service
            )
            
            render_upload_card(
                "Department Directory", 
                "departments.csv", 
                "Update RO department codes and contact emails.",
                "DEPT",
                master_service
            )

        # Recovery & Backups
        with st.expander("🛡️ Backup & Restore", expanded=False):
            st.info("System automatically creates backups before every update. You can manually restore files if needed.")
            files_dir = project_path("files")
            backups = list(files_dir.glob("*.bak_*"))
            if backups:
                backup_data = []
                for b in backups:
                    try:
                        parts = b.name.split(".bak_")
                        backup_data.append({
                            "File": parts[0],
                            "Timestamp": parts[1],
                            "Filename": b.name
                        })
                    except: continue
                
                backup_df = pd.DataFrame(backup_data)
                for _, row in backup_df.sort_values("Timestamp", ascending=False).iterrows():
                    b_col1, b_col2 = st.columns([4, 1])
                    with b_col1:
                        st.caption(f"📄 {row['File']} (Backup: {row['Timestamp']})")
                    with b_col2:
                        if st.button("🗑️", key=f"del_bak_{row['Filename']}", help=f"Delete backup {row['Filename']}"):
                            (files_dir / row['Filename']).unlink()
                            st.success("Backup deleted.")
                            st.rerun()
            else:
                st.write("No backups found yet.")

    with tabs[5]:
        render_data_table(audit_logger.to_frame(), "Audit trail", "audit_log.xlsx")

    with tabs[6]:
        st.json(get_app_settings().model_dump())
        st.divider()
        st.markdown("### Advances Scheme Mapping (3-Level)")
        scheme_path = "data/scheme_config.json"
        import json
        import os
        if os.path.exists(scheme_path):
            with open(scheme_path, 'r', encoding="utf-8") as f:
                schemes = json.load(f)
            
            new_schemes_str = st.text_area("Edit Scheme Mapping (JSON)", value=json.dumps(schemes, indent=2), height=300)
            if st.button("Update Scheme Mapping"):
                try:
                    json.loads(new_schemes_str)
                    with open(scheme_path, 'w', encoding="utf-8") as f:
                        f.write(new_schemes_str)
                    st.success("Scheme mapping updated successfully.")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
        
        st.markdown("### Role Map")
        st.json(load_yaml_config("roles.yaml"))
