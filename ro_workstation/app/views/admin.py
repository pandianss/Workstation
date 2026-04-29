import streamlit as st
import pandas as pd
from app.utils.rbac import require_role
from app.services.admin_service import (
    get_users,
    add_user,
    update_role,
    sync_ro_staff_as_users,
)
from modules.masters.engine import (
    get_master_records,
    create_master_record,
    delete_master_record,
)


from app.utils.audit import get_audit_logs

def render_admin():
    st.markdown("## Admin Panel")

    if not require_role(["ADMIN"]):
        st.error("Access denied. You do not have ADMIN privileges.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Configuration", "Master Data", "Audit Logs"])

    with tab1:
        # Automatic Sync for RO Staff
        all_staff = get_master_records("STAFF")
        import json
        ro_staff = [s for s in all_staff if str(json.loads(s.metadata_json).get("SOL")) == "3933"]
        
        newly_synced = sync_ro_staff_as_users(ro_staff)
        if newly_synced > 0:
            st.success(f"🔄 Automated Sync: {newly_synced} RO staff members have been automatically authorized as system users.")

        users = get_users()
        st.dataframe(users, use_container_width=True, hide_index=True)

        # Fetch staff records and filter by SOL 3933 (Regional Office)
        import json
        all_staff = get_master_records("STAFF")
        staff_records = []
        for r in all_staff:
            try:
                meta = json.loads(r.metadata_json)
                if str(meta.get("SOL")) == "3933":
                    staff_records.append(r)
            except:
                continue
        
        if not staff_records:
            st.warning("No Staff Master Data found for SOL 3933 (Regional Office).")
            username = st.text_input("Username (Manual Entry)")
            suggested_dept = "3933"
        else:
            staff_options = {r.code: f"{r.name_en} ({r.code})" for r in staff_records}
            username = st.selectbox(
                "Select RO Staff Member", 
                options=staff_options.keys(), 
                format_func=lambda x: staff_options[x],
                help="Only staff members assigned to the Regional Office (SOL 3933) are listed here."
            )
            suggested_dept = "3933"

        role = st.selectbox("Assign System Role", ["USER", "MANAGER", "ADMIN"])
        dept = st.text_input("Department / SOL Access", value=suggested_dept)

        if st.button("Authorize User"):
            if username:
                # Check if user already exists
                existing_users = get_users()
                if username in existing_users['username'].values:
                    st.error(f"User {username} is already authorized.")
                else:
                    add_user(username, role, dept)
                    st.success(f"Access granted to {username} successfully.")
                    st.rerun()
            else:
                st.error("Selection invalid.")

    with tab2:
        st.info("Configuration controls go here.")

    with tab3:
        st.markdown("### Master Data Management")

        with st.expander("Add New Master Record", expanded=True):
            with st.form("master_data_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                with col1:
                    category = st.selectbox(
                        "Category",
                        ["DEPARTMENT", "BRANCH", "STAFF", "USER_ROLE", "ASSET_TYPE", "DESIGNATION"],
                    )
                    code = st.text_input("Code / ID", max_chars=50)

                with col2:
                    name_en = st.text_input("Name (English)")
                    name_hi = st.text_input("Name (Hindi)")
                    name_local = st.text_input("Name (Local)")

                submit_btn = st.form_submit_button("Save Record")

                if submit_btn:
                    if not code or not name_en:
                        st.error("Code and Name (English) are required.")
                    else:
                        try:
                            create_master_record(
                                category=category,
                                code=code,
                                name_en=name_en,
                                name_hi=name_hi,
                                name_local=name_local,
                            )
                            st.success(f"Record '{code}' added successfully.")
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error(f"System Error: {e}")

        st.markdown("#### Existing Records")
        records = get_master_records()

        if not records:
            st.info("No master records found.")
        else:
            # Show summary counts for visibility
            df_counts = pd.DataFrame([{"Category": r.category} for r in records])
            summary = df_counts["Category"].value_counts().to_dict()
            summary_str = " | ".join([f"**{k}**: {v}" for k, v in summary.items()])
            st.markdown(f"📊 {summary_str}")
            data = []
            for r in records:
                data.append(
                    {
                        "ID": r.id,
                        "Category": r.category,
                        "Code": r.code,
                        "English": r.name_en,
                        "Hindi": r.name_hi,
                        "Local": r.name_local,
                        "Active": r.is_active,
                    }
                )

            df = pd.DataFrame(data)

            cats = sorted(df["Category"].unique().tolist())
            
            # Sub-tabs for logical separation
            master_tabs = st.tabs(["Branches", "Staff", "Other Masters"])
            
            with master_tabs[0]:
                branch_df = df[df["Category"] == "BRANCH"]
                if branch_df.empty:
                    st.info("No branch records found.")
                else:
                    st.dataframe(branch_df, use_container_width=True, hide_index=True)
                    
            with master_tabs[1]:
                staff_df = df[df["Category"] == "STAFF"]
                if staff_df.empty:
                    st.info("No staff records found.")
                else:
                    # For staff, we might want to show their SOL from metadata if possible
                    st.dataframe(staff_df, use_container_width=True, hide_index=True)
                    
            with master_tabs[2]:
                other_df = df[~df["Category"].isin(["BRANCH", "STAFF"])]
                if other_df.empty:
                    st.info("No other master records found.")
                else:
                    selected_sub_cat = st.selectbox("Filter Other Categories", ["ALL"] + sorted(other_df["Category"].unique().tolist()))
                    if selected_sub_cat != "ALL":
                        other_df = other_df[other_df["Category"] == selected_sub_cat]
                    st.dataframe(other_df, use_container_width=True, hide_index=True)

            with st.expander("Delete Record"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    options = {
                        r["ID"]: f"{r['Category']} - {r['Code']} ({r['English']})"
                        for r in df.to_dict("records")
                    }
                    del_id = st.selectbox(
                        "Select record to delete",
                        options=options.keys(),
                        format_func=lambda x: options[x],
                    )
                with col_del_2:
                    if st.button("Delete Selected"):
                        if delete_master_record(del_id):
                            st.success("Record deleted.")
                            st.rerun()
                        else:
                            st.error("Deletion failed.")

        with st.expander("View Extended Details"):
            options_view = {
                r.id: f"{r.category} - {r.code} ({r.name_en})"
                for r in records
            }
            selected_id = st.selectbox(
                "Select record to view full details",
                options=options_view.keys(),
                format_func=lambda x: options_view[x],
                key="view_meta_select"
            )
            
            selected_record = next((r for r in records if r.id == selected_id), None)
            if selected_record and selected_record.metadata_json:
                import json
                try:
                    meta = json.loads(selected_record.metadata_json)
                    
                    # 1. Trilingual Address Section (High Priority)
                    if any(k in meta for k in ["address", "addressHi", "addressTa"]):
                        st.markdown("##### 📍 Branch Address (Trilingual)")
                        cols = st.columns(3)
                        cols[0].write(f"**English:**\n{meta.get('address', 'N/A')}")
                        cols[1].write(f"**Hindi:**\n{meta.get('addressHi', 'N/A')}")
                        cols[2].write(f"**Local:**\n{meta.get('addressTa', 'N/A')}")
                        st.markdown("---")

                    # 2. Other Metadata
                    meta_data = []
                    address_keys = ["address", "addressHi", "addressTa"]
                    for k, v in meta.items():
                        if k in address_keys: continue # Already shown above
                        if v and str(v).strip() and str(v).lower() != 'nan':
                            meta_data.append({"Field": k, "Value": str(v)})
                    
                    if meta_data:
                        st.markdown(f"##### 📋 Additional Metadata for {selected_record.name_en}")
                        st.table(pd.DataFrame(meta_data))
                    else:
                        st.info("No further details found.")
                except Exception as e:
                    st.error(f"Error parsing details: {e}")

            else:
                st.info("No extended details available for this record.")



    with tab4:
        st.markdown("### System Audit Logs")
        st.caption("Monitoring real-time activity across the workstation.")
        
        logs_df = get_audit_logs()
        
        if logs_df.empty:
            st.info("No audit logs found.")
        else:
            # Simple search filter
            search = st.text_input("Search Logs", placeholder="e.g. username or action type")
            if search:
                logs_df = logs_df[
                    logs_df['User'].str.contains(search, case=False) | 
                    logs_df['Action'].str.contains(search, case=False)
                ]
            
            st.dataframe(logs_df, use_container_width=True, hide_index=True)
            
            if st.button("Refresh Logs"):
                st.rerun()

