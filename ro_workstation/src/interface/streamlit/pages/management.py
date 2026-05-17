import streamlit as st
import pandas as pd
import datetime
from src.interface.streamlit.components.primitives import render_action_bar, render_premium_metrics
from src.application.services.master_service import MasterService
from src.core.paths import project_path

def render():
    master_service = MasterService()
    render_action_bar("Master Management Center", ["Data Integrity", "Secure Sync", "Audit Ready"])
    
    st.markdown("### 👥 Regional Master Registry")
    st.caption("Securely update staff, branch, and department masters using the file uploaders below.")
    
    # ─── SYNC STATUS ──────────────────────────────────────────────────────
    status = master_service.repo.get_all()
    metrics = {
        "Staff Records": len([r for r in status if r.category == "STAFF"]),
        "Active Units": len([r for r in status if r.category == "UNIT" and r.is_active]),
        "Departments": len([r for r in status if r.category == "DEPT"]),
        "Last Sync": datetime.datetime.now().strftime("%H:%M") # Mock for now
    }
    render_premium_metrics(metrics)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── MASTER UPLOADERS ─────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    
    with col1:
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

    with col2:
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

    # ─── RECOVERY & BACKUPS ───────────────────────────────────────────────
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

def render_upload_card(title, expected_name, description, category, service):
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

if __name__ == "__main__":
    render()
