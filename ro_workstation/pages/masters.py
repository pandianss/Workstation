import streamlit as st
import pandas as pd
from modules.masters.engine import (
    get_master_records, 
    create_master_record, 
    update_master_record, 
    delete_master_record
)
from modules.ui.theme import render_hero, render_panel

st.set_page_config(page_title="Master Data Hub", page_icon="🗃️", layout="wide")

st.markdown("""
<style>
.master-header {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #1b5960;
}
.lang-badge {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.3rem;
    background: rgba(47, 127, 112, 0.15);
    color: #1b5960;
}
</style>
""", unsafe_allow_html=True)

render_hero(
    "Master Data Management",
    "Maintain centralized, trilingual records for the entire regional office.",
    "System Administration",
    ["English", "हिंदी", "தமிழ் (Local)"]
)

# Categories
CATEGORIES = [
    "DEPARTMENT", 
    "BRANCH", 
    "USER_ROLE", 
    "GRADE", 
    "DESIGNATION", 
    "ASSET_ATM", 
    "ASSET_LOCKER", 
    "ASSET_OTHER"
]

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('<div class="ro-panel">', unsafe_allow_html=True)
    st.markdown("### Categories")
    selected_category = st.radio("Select Category", CATEGORIES, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="ro-panel">', unsafe_allow_html=True)
    
    tab_view, tab_add = st.tabs([f"View {selected_category}s", f"Add New {selected_category}"])
    
    with tab_view:
        records = get_master_records(selected_category)
        if records:
            # Create a dataframe for display
            df_data = []
            for r in records:
                df_data.append({
                    "ID": r.id,
                    "Code": r.code,
                    "English": r.name_en,
                    "Hindi (हिंदी)": r.name_hi,
                    "Local (தமிழ்)": r.name_local,
                    "Status": "Active" if r.is_active else "Inactive"
                })
            
            df = pd.DataFrame(df_data)
            
            # Display stats
            active_count = sum(1 for r in records if r.is_active)
            st.markdown(f"<div class='ro-eyebrow'>{len(records)} Total &nbsp;&bull;&nbsp; {active_count} Active</div>", unsafe_allow_html=True)
            
            # Data table
            st.dataframe(
                df.drop(columns=["ID"]),
                use_container_width=True,
                hide_index=True
            )
            
            # Edit/Delete Section
            st.markdown("---")
            st.markdown("<div class='master-header'>Quick Actions</div>", unsafe_allow_html=True)
            
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                edit_id = st.selectbox("Select record to edit/toggle", options=[r.id for r in records], format_func=lambda x: next((f"{r.code} - {r.name_en}" for r in records if r.id == x), x))
            
            if edit_id:
                sel_record = next(r for r in records if r.id == edit_id)
                with edit_col2:
                    st.write("")
                    st.write("")
                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        toggle_label = "Deactivate" if sel_record.is_active else "Activate"
                        if st.button(toggle_label, use_container_width=True):
                            update_master_record(edit_id, is_active=not sel_record.is_active)
                            st.success(f"Record {toggle_label}d!")
                            st.rerun()
                    with action_col2:
                        if st.button("Delete (Irreversible)", type="primary", use_container_width=True):
                            delete_master_record(edit_id)
                            st.success("Record deleted!")
                            st.rerun()
                            
        else:
            st.info(f"No records found for category: {selected_category}")
            
    with tab_add:
        st.markdown(f"### Create New {selected_category}")
        with st.form("add_master_form", clear_on_submit=True):
            code_input = st.text_input("Code (Unique ID)*", max_chars=20)
            
            st.markdown("<div class='master-header' style='margin-top: 1rem;'>Trilingual Names</div>", unsafe_allow_html=True)
            en_input = st.text_input("English Name*")
            hi_input = st.text_input("Hindi Name (हिंदी)")
            loc_input = st.text_input("Local Language Name (தமிழ்)")
            
            is_active_input = st.checkbox("Set as Active", value=True)
            
            submitted = st.form_submit_button("Save Master Record")
            
            if submitted:
                if not code_input or not en_input:
                    st.error("Code and English Name are required.")
                else:
                    try:
                        create_master_record(
                            category=selected_category,
                            code=code_input.strip(),
                            name_en=en_input.strip(),
                            name_hi=hi_input.strip(),
                            name_local=loc_input.strip()
                        )
                        # We also update the active status immediately if they unchecked it
                        if not is_active_input:
                            # fetch it again to update
                            recs = get_master_records(selected_category)
                            new_rec = next((r for r in recs if r.code == code_input.strip()), None)
                            if new_rec:
                                update_master_record(new_rec.id, is_active=False)
                        st.success("Record created successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                        
    st.markdown('</div>', unsafe_allow_html=True)
