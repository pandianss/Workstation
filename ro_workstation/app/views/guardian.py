import streamlit as st
import pandas as pd
import json
from app.services.admin_service import get_sorted_users
from app.services.guardian_service import record_followup, get_followups
from modules.masters.engine import get_master_records

def render_guardian_view():
    st.markdown("## 🛡️ Guardian Officer Dashboard")
    
    username = st.session_state.get("username")
    role = st.session_state.get("role")
    
    # 1. Access Control Check
    users_df = get_sorted_users() 
    user_record = users_df[users_df["username"] == username]
    
    if user_record.empty:
        st.error("User record not found. Please contact Admin.")
        return

    assigned_sols = user_record.iloc[0].get("assigned_branches", [])
    if not isinstance(assigned_sols, list):
        assigned_sols = []
    
    # 2. View Routing
    if role == "ADMIN":
        manage_tab, my_tab, request_tab = st.tabs(["📊 Management Overview", "🛡️ My Assigned Branches", "✍️ Raise Request"])
    else:
        my_tab, request_tab = st.tabs(["🛡️ My Assigned Branches", "✍️ Raise Request"])
        manage_tab = None

    if manage_tab:
        with manage_tab:
            st.markdown("### Regional Oversight")
            
            # 1. Allocation Mapping
            with st.expander("📋 Current Guardian Allocations", expanded=True):
                all_users = get_sorted_users()
                alloc_data = []
                for idx, row in all_users.iterrows():
                    assigned = row.get("assigned_branches", [])
                    if not isinstance(assigned, list): assigned = []
                    if assigned:
                        for sol in assigned:
                            alloc_data.append({
                                "Guardian Officer": f"{row.get('name')} ({row['username']})",
                                "Branch SOL": sol,
                                "Designation": row.get("designation")
                            })
                
                if alloc_data:
                    st.dataframe(pd.DataFrame(alloc_data), use_container_width=True, hide_index=True)
                else:
                    st.info("No branches allocated yet.")

            # 2. Activity Feed
            st.markdown("---")
            st.markdown("### 📅 Daily Activity Log")
            all_followups = get_followups()
            if not all_followups:
                st.info("No follow-up records found.")
            else:
                f_df = pd.DataFrame(all_followups)
                f_df = f_df.sort_values("timestamp", ascending=False)
                m1, m2, m3 = st.columns(3)
                m1.metric("Today's Entries", len(f_df[f_df["date"] == pd.Timestamp.now().strftime("%Y-%m-%d")]))
                m2.metric("Total Branches Monitored", f_df["sol"].nunique())
                m3.metric("Reporting Officers", f_df["go_username"].nunique())
                
                st.dataframe(
                    f_df[["date", "sol", "go_username", "details"]].rename(columns={
                        "sol": "Branch", "go_username": "Officer", "details": "Comment"
                    }),
                    use_container_width=True, hide_index=True
                )

    with my_tab:
        if not assigned_sols:
            st.info("You are not currently assigned as a Guardian Officer for any branches.")
        else:
            st.markdown(f"### My Monitoring Desk ({len(assigned_sols)} Branches)")
            all_branches = get_master_records("BRANCH")
            branch_map = {b.code: b for b in all_branches}
            
            for sol in assigned_sols:
                branch = branch_map.get(sol)
                branch_name = branch.name_en if branch else f"Branch {sol}"
                
                with st.expander(f"📍 {branch_name} ({sol})", expanded=False):
                    if branch:
                        meta = json.loads(branch.metadata_json)
                        st.caption(f"Type: {meta.get('Type')} | {branch.name_hi} | {branch.name_local}")
                    
                    history = get_followups(sol=sol)
                    if history:
                        st.markdown("**History:**")
                        h_df = pd.DataFrame(history).sort_values("timestamp", ascending=False)
                        st.dataframe(h_df[["date", "details"]].head(3), use_container_width=True, hide_index=True)
                    
                    with st.form(f"go_form_{sol}"):
                        st.markdown("**1. Record Monitoring Entry**")
                        details = st.text_area("Observations", key=f"go_text_{sol}")
                        
                        st.markdown("---")
                        st.markdown("**2. Raise Follow-up Request (Optional)**")
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            dept_records = get_master_records("DEPARTMENT")
                            dept_options = {r.code: f"{r.name_en} ({r.code})" for r in dept_records}
                            target_dept = st.selectbox("Target Department", options=["None"] + list(dept_options.keys()), format_func=lambda x: dept_options.get(x, "No Request"))
                        with col_r2:
                            all_ro_users = get_sorted_users()
                            target_user = st.selectbox("Assign to Officer", options=["None"] + all_ro_users["username"].tolist(), format_func=lambda x: f"{all_ro_users[all_ro_users['username']==x]['name'].iloc[0]} ({x})" if x != "None" else "No Assignee")
                        
                        prio = st.select_slider("Priority", options=["P4", "P3", "P2", "P1"], value="P3")

                        if st.form_submit_button("Submit Entry & Request"):
                            if details: record_followup(username, sol, details)
                            if target_dept != "None" and target_user != "None":
                                from modules.tasks.engine import create_task
                                create_task(title=f"GO Request: {branch_name}", dept=target_dept, assigned_to=target_user, priority=prio, description=details)
                                st.toast("Request Sent!")
                            st.rerun()

    if request_tab:
        with request_tab:
            st.markdown("### Regional Follow-up Desk")
            st.caption("Raise a direct follow-up request for any branch in the region.")
            
            with st.form("regional_request_form"):
                col_rr1, col_rr2 = st.columns(2)
                with col_rr1:
                    branch_recs = get_master_records("BRANCH")
                    branch_opts = {b.code: f"{b.name_en} ({b.code})" for b in branch_recs}
                    
                    # Define broad scope options
                    scope_options = {
                        "GENERIC": "📁 Generic (General Request)",
                        "ALL_GO": "📢 Broadcast to ALL Guardian Officers",
                        "TYPE_METRO": "🏙️ All METRO Branches",
                        "TYPE_URBAN": "🏢 All URBAN Branches",
                        "TYPE_SEMI_URBAN": "🏘️ All SEMI-URBAN Branches",
                        "TYPE_RURAL": "🌾 All RURAL Branches"
                    }
                    
                    sel_sol = st.selectbox(
                        "Select Branch / Scope", 
                        options=list(scope_options.keys()) + list(branch_opts.keys()), 
                        format_func=lambda x: scope_options.get(x, branch_opts.get(x))
                    )
                    
                    dept_recs = get_master_records("DEPARTMENT")
                    dept_opts = {r.code: f"{r.name_en} ({r.code})" for r in dept_recs}
                    t_dept = st.selectbox("Target Department", options=list(dept_opts.keys()), format_func=lambda x: dept_opts[x])
                with col_rr2:
                    all_u = get_sorted_users()
                    
                    # For broadcast/type, we might not need a specific 'Target User' 
                    # but I'll keep it as a 'Point of Contact' or default to Dept Head.
                    t_user = st.selectbox("Assign to Officer", options=all_u["username"].tolist(), format_func=lambda x: f"{all_u[all_u['username']==x]['name'].iloc[0]} ({x})")
                    t_prio = st.select_slider("Priority Level", options=["P4", "P3", "P2", "P1"], value="P3")

                r_details = st.text_area("Request Details")
                if st.form_submit_button("🚀 Dispatch Request"):
                    if r_details:
                        from modules.tasks.engine import create_task
                        
                        target_users = [t_user]
                        title_prefix = "Follow-up"
                        
                        # Handle Broad Scopes
                        if sel_sol == "ALL_GO":
                            target_users = all_u[all_u["assigned_branches"].apply(lambda x: isinstance(x, list) and len(x) > 0)]["username"].tolist()
                            title_prefix = "BROADCAST"
                            pop_group = sel_sol.replace("TYPE_", "").replace("_", " ")
                            # Find branches in this group
                            target_sols = [b.code for b in branch_recs if json.loads(b.metadata_json).get("populationGroup") == pop_group]
                            # Find GOs assigned to these branches
                            target_users = []
                            for idx, row in all_u.iterrows():
                                u_assigned = row.get("assigned_branches", [])
                                if any(sol in target_sols for sol in u_assigned):
                                    target_users.append(row["username"])
                            title_prefix = f"SCOPE: {pop_group}"
                            if not target_users: target_users = [t_user] # Fallback

                        # Create tasks
                        unique_targets = list(set(target_users))
                        for target in unique_targets:
                            branch_name = branch_opts.get(sel_sol, scope_options.get(sel_sol, "General"))
                            create_task(
                                title=f"{title_prefix}: {branch_name}", 
                                dept=t_dept, 
                                assigned_to=target, 
                                priority=t_prio, 
                                description=f"Raised via Regional Follow-up Desk.\n\nDetails: {r_details}"
                            )
                        
                        st.success(f"Request successfully dispatched to {len(unique_targets)} officer(s).")
                        st.toast("Request Sent!")
                    else:
                        st.error("Please provide details.")
