import streamlit as st
import pandas as pd
import json
import datetime
from src.core.paths import project_path
from src.interface.streamlit.components.primitives import render_action_bar, render_premium_metrics
from src.application.services.document.office_note_service import OfficeNoteService
from src.application.services.circular_service import CircularService
from src.interface.streamlit.state.services import get_doc_service_v4
from src.application.use_cases.mis.service import MISAnalyticsService

def render():
    render_action_bar("Unified Archive Hub", ["Audit Ready", "Searchable", "Centralized"])
    
    note_service = OfficeNoteService()
    circ_service = CircularService()
    mis_service = MISAnalyticsService()
    doc_service = get_doc_service_v4()
    
    # ─── REPOSITORY STATS ──────────────────────────────────────────────────
    notes_df = note_service.get_all()
    circs = circ_service.get_all()
    
    metrics = {
        "Office Notes": len(notes_df),
        "Circulars": len(circs),
        "Total Documents": len(notes_df) + len(circs),
        "Last Entry": "Today" # Placeholder
    }
    render_premium_metrics(metrics)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── SEARCH & FILTERS ─────────────────────────────────────────────────
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        doc_type = st.selectbox("Document Type", ["All Types", "Office Note", "Circular", "MIS Data Feed"])
    with f_col2:
        status_filter = st.selectbox("Status", ["All", "DRAFT", "FINALIZED", "PUBLISHED"])
    with f_col3:
        search_query = st.text_input("Global Search", placeholder="Search by title, ref no, or content...")

    # ─── UNIFIED DATASET ──────────────────────────────────────────────────
    unified_data = []
    
    # Process Notes
    if not notes_df.empty:
        for _, row in notes_df.iterrows():
            unified_data.append({
                "ID": row["id"],
                "Source": "Office Note",
                "Type": row["type"],
                "Title": row["titleEn"],
                "Ref No": row["referenceNo"],
                "Status": row["status"],
                "Date": row["createdAt"],
                "Dept": row["dept"],
                "RAW": row.to_dict()
            })
            
    # Process Circulars
    for c in circs:
        unified_data.append({
            "ID": c.get("id"),
            "Source": "Circular",
            "Type": "CIRCULAR",
            "Title": c.get("subject"),
            "Ref No": c.get("number") or c.get("ref_no"),
            "Status": "PUBLISHED",
            "Date": c.get("created_at") or c.get("date"),
            "Dept": c.get("dept"),
            "RAW": c
        })

    # Process MIS Files
    mis_archive = project_path("data", "mis", "archive")
    if mis_archive.exists():
        for f in mis_archive.glob("*.xlsx"):
            unified_data.append({
                "ID": f.name,
                "Source": "MIS Data Feed",
                "Type": "EXCEL_DATA",
                "Title": f.name,
                "Ref No": "N/A",
                "Status": "INGESTED",
                "Date": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "Dept": "MIS",
                "RAW": {"filename": f.name, "path": str(f)}
            })
        
    df = pd.DataFrame(unified_data)
    if df.empty:
        st.warning("No documents found in the archive.")
        return

    # Apply Filters
    if doc_type != "All Types":
        df = df[df["Source"] == doc_type]
    if status_filter != "All":
        df = df[df["Status"] == status_filter]
    if search_query:
        df = df[
            df["Title"].str.contains(search_query, case=False, na=False) |
            df["Ref No"].astype(str).str.contains(search_query, case=False, na=False)
        ]

    # ─── ARCHIVE TABLE ────────────────────────────────────────────────────
    st.markdown(f"#### Results ({len(df)})")
    
    display_df = df[["Source", "Title", "Ref No", "Status", "Date", "Dept"]].copy()
    display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce", format="mixed").dt.strftime("%d-%b-%Y %H:%M")
    
    selection = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="archive_table"
    )

    if selection.selection.rows:
        idx = selection.selection.rows[0]
        selected_doc = df.iloc[idx]
        render_doc_manager(selected_doc, note_service, circ_service, mis_service, doc_service)

def render_doc_manager(doc, note_service, circ_service, mis_service, doc_service):
    st.divider()
    st.subheader(f"🛠️ Manager: {doc['Title']}")
    
    m_col1, m_col2 = st.columns([2, 1])
    
    with m_col1:
        with st.container(border=True):
            st.markdown(f"**Source Repository:** `{doc['Source']}`")
            st.markdown(f"**Reference Number:** `{doc['Ref No']}`")
            st.markdown(f"**Department:** {doc['Dept']}")
            st.markdown("---")
            if doc["Source"] == "Office Note":
                st.json(doc["RAW"].get("parsed_content", {}))
            else:
                st.json(doc["RAW"])

    with m_col2:
        st.markdown("#### Actions")
        if st.button("📄 View / Regenerate PDF", use_container_width=True, type="primary"):
            st.info("Regeneration engine warming up...")
            # Logic here for PDF generation (similar to office_note_hub)
            
        if st.button("✏️ Edit Metadata", use_container_width=True):
            st.session_state[f"edit_archive_{doc['ID']}"] = True
            st.rerun()
            
        if st.button("🗑️ Delete Permanently", use_container_width=True, type="secondary"):
            with st.spinner("Deleting document..."):
                if doc["Source"] == "Office Note":
                    success = note_service.delete_note(doc["ID"])
                elif doc["Source"] == "MIS Data Feed":
                    success = mis_service.delete_mis_file(doc["ID"])
                else:
                    # Implement circular delete if needed
                    success = False
                
                if success:
                    st.success("Document deleted successfully.")
                    st.rerun()
                else:
                    st.error("Delete failed or not implemented for this type.")

if __name__ == "__main__":
    render()
