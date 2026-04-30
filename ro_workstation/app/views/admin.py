import json

import pandas as pd
import streamlit as st

from app.services.admin_service import (
    get_sorted_users,
    sync_ro_staff_as_users,
    update_user_access,
    update_user_guardian_branches,
)
from app.services.config_service import get_config, update_config
from app.utils.audit import get_audit_logs, log_action
from app.utils.rbac import require_role
from modules.masters.engine import (
    create_master_record,
    delete_master_record,
    get_master_records,
    update_master_record,
)

MASTER_CATEGORIES = ["DEPARTMENT", "BRANCH", "STAFF", "USER_ROLE", "ASSET_TYPE", "DESIGNATION"]


def _load_ro_staff():
    staff_records = get_master_records("STAFF")
    ro_staff = []
    for staff in staff_records:
        try:
            metadata = json.loads(staff.metadata_json or "{}")
        except json.JSONDecodeError:
            metadata = {}
        sol = str(metadata.get("SOL", "")).strip()
        if sol in {"3933", "4069"}:
            ro_staff.append(staff)
    return ro_staff


def _render_summary(users_df, records, logs_df):
    departments = len([record for record in records if record.category == "DEPARTMENT"])
    branches = len([record for record in records if record.category == "BRANCH"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Authorized Users", len(users_df))
    col2.metric("Departments", departments)
    col3.metric("Branches", branches)
    col4.metric("Audit Events", len(logs_df))


def _render_user_directory(users_df):
    st.markdown("### User Directory")
    st.caption("Review the current RO hierarchy, roles, and department access in one place.")

    search = st.text_input("Search Users", placeholder="Search by username, name, role, or designation")
    directory_df = users_df.copy()

    if search:
        query = search.lower()
        directory_df = directory_df[
            directory_df.apply(
                lambda row: query in " ".join(
                    [
                        str(row.get("username", "")),
                        str(row.get("name", "")),
                        str(row.get("role", "")),
                        str(row.get("designation", "")),
                        ", ".join(row.get("depts", [])) if isinstance(row.get("depts"), list) else str(row.get("depts", "")),
                    ]
                ).lower(),
                axis=1,
            )
        ]

    display_df = directory_df[["username", "name", "designation", "role", "depts", "grade"]].copy()
    display_df["depts"] = display_df["depts"].apply(
        lambda value: ", ".join(value) if isinstance(value, list) else str(value)
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def _render_access_editor(users_df):
    st.markdown("### Access Editor")
    st.caption("Update the selected user’s role and department coverage from a single workspace.")

    selected_user = st.selectbox(
        "Select User",
        options=users_df["username"].tolist(),
        format_func=lambda username: f"{users_df[users_df['username'] == username]['name'].iloc[0]} ({username})",
    )
    selected_row = users_df[users_df["username"] == selected_user].iloc[0]

    dept_records = get_master_records("DEPARTMENT")
    dept_options = {record.code: f"{record.name_en} ({record.code})" for record in dept_records}
    existing_depts = selected_row.get("depts", [])
    if not isinstance(existing_depts, list):
        existing_depts = [selected_row.get("dept", "ALL")]
    valid_defaults = [dept for dept in existing_depts if dept in dept_options]

    with st.form("user_access_editor"):
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Role", ["ADMIN", "MANAGER", "USER"], index=["ADMIN", "MANAGER", "USER"].index(selected_row["role"]))
        with col2:
            depts = st.multiselect(
                "Department Access",
                options=list(dept_options.keys()),
                default=valid_defaults,
                format_func=lambda code: dept_options[code],
                help="Users can be mapped to one or more departments.",
            )

        submitted = st.form_submit_button("Save Access Settings")

        if submitted:
            if not depts:
                st.error("Assign at least one department before saving.")
            else:
                updated = update_user_access(selected_user, role=role, depts=depts)
                if updated:
                    log_action(st.session_state.get("username", "system"), f"Updated access for {selected_user}")
                    st.success(f"Access updated for {selected_user}.")
                    st.rerun()
                else:
                    st.error("User update failed.")


def _render_guardian_assignments(users_df):
    st.markdown("### Guardian Coverage")
    st.caption("Assign monitoring branches to desk officers without leaving the access-control area.")

    guardian_candidates = users_df[users_df["rank"] == 4]
    if guardian_candidates.empty:
        st.info("No eligible desk officers are currently available for branch coverage.")
        return

    branch_records = get_master_records("BRANCH")
    branch_options = {record.code: f"{record.name_en} ({record.code})" for record in branch_records}

    selected_user = st.selectbox(
        "Guardian Officer",
        options=guardian_candidates["username"].tolist(),
        format_func=lambda username: f"{guardian_candidates[guardian_candidates['username'] == username]['name'].iloc[0]} ({username})",
        key="guardian_user",
    )
    selected_row = guardian_candidates[guardian_candidates["username"] == selected_user].iloc[0]

    assigned_branches = selected_row.get("assigned_branches", [])
    if not isinstance(assigned_branches, list):
        assigned_branches = []
    valid_defaults = [branch for branch in assigned_branches if branch in branch_options]

    with st.form("guardian_assignment_form"):
        new_assignment = st.multiselect(
            "Assigned Branches",
            options=list(branch_options.keys()),
            default=valid_defaults,
            format_func=lambda code: branch_options[code],
        )
        submitted = st.form_submit_button("Save Guardian Coverage")

        if submitted:
            updated = update_user_guardian_branches(selected_user, new_assignment)
            if updated:
                log_action(st.session_state.get("username", "system"), f"Updated guardian coverage for {selected_user}")
                st.success(f"Guardian coverage updated for {selected_user}.")
                st.rerun()
            else:
                st.error("Guardian assignment update failed.")


def _render_system_settings():
    st.markdown("### System Settings")
    st.caption("Keep the operational defaults and admin security settings together in one place.")

    config = get_config()
    col1, col2 = st.columns(2)

    with col1:
        with st.form("general_settings_form"):
            st.markdown("#### General")
            theme = st.selectbox("Theme", ["light", "dark"], index=0 if config.get("theme", "light") == "light" else 1)
            max_tasks = st.number_input(
                "Max Tasks Displayed",
                min_value=10,
                max_value=1000,
                value=int(config.get("max_tasks_displayed", 100)),
                step=10,
            )
            if st.form_submit_button("Save General Settings"):
                update_config({"theme": theme, "max_tasks_displayed": int(max_tasks)})
                log_action(st.session_state.get("username", "system"), "Updated general settings")
                st.success("General settings saved.")
                st.rerun()

    with col2:
        with st.form("security_settings_form"):
            st.markdown("#### Security")
            admin_password = st.text_input(
                "Admin Override Password",
                value=config.get("admin_password", "admin"),
                type="password",
            )
            if st.form_submit_button("Save Security Settings"):
                update_config({"admin_password": admin_password})
                log_action(st.session_state.get("username", "system"), "Updated admin password")
                st.success("Security settings saved.")
                st.rerun()


def _render_master_registry(records):
    st.markdown("### Master Registry")
    st.caption("Manage reference data through dedicated workflows instead of a single overloaded block.")

    records_df = pd.DataFrame(
        [
            {
                "ID": record.id,
                "Category": record.category,
                "Code": record.code,
                "English": record.name_en,
                "Hindi": record.name_hi,
                "Local": record.name_local,
                "Active": record.is_active,
                "Metadata": record.metadata_json,
            }
            for record in records
        ]
    )

    overview_tab, add_tab, maintain_tab, details_tab = st.tabs(
        ["Overview", "Add Record", "Maintain Records", "Extended Details"]
    )

    with overview_tab:
        if records_df.empty:
            st.info("No master records found.")
        else:
            summary = records_df["Category"].value_counts().reset_index()
            summary.columns = ["Category", "Count"]

            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(summary, use_container_width=True, hide_index=True)
            with col2:
                selected_category = st.selectbox("Browse Category", ["ALL"] + sorted(records_df["Category"].unique().tolist()))
                filtered_df = records_df if selected_category == "ALL" else records_df[records_df["Category"] == selected_category]
                st.dataframe(
                    filtered_df[["Category", "Code", "English", "Hindi", "Local", "Active"]],
                    use_container_width=True,
                    hide_index=True,
                )

    with add_tab:
        with st.form("master_record_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Category", MASTER_CATEGORIES)
                code = st.text_input("Code / ID", max_chars=50)
            with col2:
                name_en = st.text_input("Name (English)")
                name_hi = st.text_input("Name (Hindi)")
                name_local = st.text_input("Name (Local)")
                
                # DOB for Staff
                dob = None
                if category == "STAFF":
                    dob = st.date_input("Date of Birth", value=None, help="Used for birthday reminders on the dashboard")

            if st.form_submit_button("Add Master Record"):
                if not code or not name_en:
                    st.error("Code and English name are required.")
                else:
                    try:
                        create_master_record(
                            category=category,
                            code=code,
                            name_en=name_en,
                            name_hi=name_hi,
                            name_local=name_local,
                            metadata_dict={"dob": dob.isoformat() if dob else None}
                        )
                        log_action(st.session_state.get("username", "system"), f"Created master record {category}:{code}")
                        st.success(f"Record '{code}' created successfully.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                    except Exception as exc:
                        st.error(f"System error: {exc}")

    with maintain_tab:
        if records_df.empty:
            st.info("No records available for maintenance.")
        else:
            manage_category = st.selectbox("Category To Maintain", MASTER_CATEGORIES)
            category_rows = records_df[records_df["Category"] == manage_category].to_dict("records")

            if not category_rows:
                st.info(f"No records found in {manage_category}.")
            else:
                col1, col2 = st.columns(2)

                with col1:
                    selected_edit = st.selectbox(
                        "Record To Edit",
                        options=category_rows,
                        format_func=lambda row: f"{row['English']} ({row['Code']})",
                    )
                    with st.form("edit_master_record_form"):
                        new_en = st.text_input("Name (English)", value=selected_edit["English"] or "")
                        new_hi = st.text_input("Name (Hindi)", value=selected_edit["Hindi"] or "")
                        new_local = st.text_input("Name (Local)", value=selected_edit["Local"] or "")
                        
                        # DOB for Staff
                        new_dob = None
                        if manage_category == "STAFF":
                            current_meta = json.loads(selected_edit["Metadata"]) if selected_edit["Metadata"] else {}
                            current_dob = current_meta.get("dob")
                            import datetime
                            try:
                                default_dob = datetime.date.fromisoformat(current_dob) if current_dob else None
                            except:
                                default_dob = None
                            new_dob = st.date_input("Date of Birth", value=default_dob)
                        if st.form_submit_button("Update Record"):
                            updated = update_master_record(
                                selected_edit["ID"],
                                name_en=new_en,
                                name_hi=new_hi,
                                name_local=new_local,
                                metadata_dict={"dob": new_dob.isoformat() if new_dob else None}
                            )
                            if updated:
                                log_action(st.session_state.get("username", "system"), f"Updated master record {selected_edit['Category']}:{selected_edit['Code']}")
                                st.toast(f"✅ {selected_edit['Code']} updated")
                                st.success(f"Changes for '{new_en}' saved successfully.")
                                import time
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Record update failed.")

                with col2:
                    selected_delete = st.selectbox(
                        "Record To Delete",
                        options=category_rows,
                        format_func=lambda row: f"{row['English']} ({row['Code']})",
                        key="delete_master_record_select",
                    )
                    st.warning("Deletion is permanent and should be used carefully.")
                    if st.button("Delete Selected Record", type="secondary"):
                        deleted = delete_master_record(selected_delete["ID"])
                        if deleted:
                            log_action(st.session_state.get("username", "system"), f"Deleted master record {selected_delete['Category']}:{selected_delete['Code']}")
                            st.toast(f"🗑️ {selected_delete['Code']} removed")
                            st.success(f"Successfully deleted {selected_delete['English']}.")
                            import time
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Delete failed.")

    with details_tab:
        if not records:
            st.info("No extended details available.")
        else:
            options = {
                record.id: f"{record.category} - {record.code} ({record.name_en})"
                for record in records
            }
            selected_id = st.selectbox(
                "Select Record",
                options=options.keys(),
                format_func=lambda record_id: options[record_id],
            )
            selected_record = next((record for record in records if record.id == selected_id), None)

            if selected_record and selected_record.metadata_json:
                try:
                    metadata = json.loads(selected_record.metadata_json)
                    if metadata:
                        st.json(metadata)
                    else:
                        st.info("No extended metadata found for this record.")
                except json.JSONDecodeError as exc:
                    st.error(f"Could not parse metadata: {exc}")
            else:
                st.info("No extended metadata found for this record.")


def _render_audit_trail(logs_df):
    st.markdown("### Audit Trail")
    st.caption("Search administrative activity without leaving the monitoring view.")

    if logs_df.empty:
        st.info("No audit logs found.")
        return

    search = st.text_input("Search Audit Logs", placeholder="Search by user or action")
    filtered_logs = logs_df.copy()
    if search:
        filtered_logs = filtered_logs[
            filtered_logs["User"].str.contains(search, case=False, na=False)
            | filtered_logs["Action"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(filtered_logs, use_container_width=True, hide_index=True)
    if st.button("Refresh Audit Trail"):
        st.rerun()


def render_admin():
    st.markdown("## Admin Console")

    if not require_role(["ADMIN"]):
        st.error("Access denied. You do not have ADMIN privileges.")
        return

    synced_count = sync_ro_staff_as_users(_load_ro_staff())
    if synced_count:
        st.success(f"Synchronized {synced_count} staff profile(s) into user access control.")

    users_df = get_sorted_users()
    master_records = get_master_records()
    logs_df = get_audit_logs()

    _render_summary(users_df, master_records, logs_df)
    st.markdown("---")

    access_tab, settings_tab, registry_tab, audit_tab = st.tabs(
        ["Access Control", "System Settings", "Master Registry", "Audit Trail"]
    )

    with access_tab:
        subtab1, subtab2, subtab3 = st.tabs(["User Directory", "Access Editor", "Guardian Coverage"])
        with subtab1:
            _render_user_directory(users_df)
        with subtab2:
            _render_access_editor(users_df)
        with subtab3:
            _render_guardian_assignments(users_df)

    with settings_tab:
        _render_system_settings()

    with registry_tab:
        _render_master_registry(master_records)

    with audit_tab:
        _render_audit_trail(logs_df)
