from __future__ import annotations

import datetime
import pandas as pd
import streamlit as st

from src.application.services.document_service import DocumentService
from src.application.services.task_service import TaskService
from src.application.services.mail_merge_service import MailMergeService
from src.application.use_cases.knowledge.indexing import KnowledgeIndexingService, SUPPORTED_EXTENSIONS
from src.application.use_cases.knowledge.qa import KnowledgeQaService
from src.application.use_cases.knowledge.search import KnowledgeSearchService
from src.interface.streamlit.components.primitives import render_action_bar, render_chart_container, render_data_table, render_filter_panel


@st.cache_resource
def get_task_service():
    return TaskService()

@st.cache_resource
def get_indexing_service():
    return KnowledgeIndexingService()

@st.cache_resource
def get_qa_service():
    return KnowledgeQaService()

@st.cache_resource
def get_search_service():
    return KnowledgeSearchService()

@st.cache_resource
def get_doc_service():
    return DocumentService()

@st.cache_resource
def get_mail_merge_service():
    return MailMergeService()


def render() -> None:
    task_service = get_task_service()
    indexing_service = get_indexing_service()
    qa_service = get_qa_service()
    search_service = get_search_service()
    doc_service = get_doc_service()
    mm_service = get_mail_merge_service()

    render_action_bar("Document Center", ["Office Notes", "Mail Merge", "Official Correspondence"])
    tabs = st.tabs(["Task Analytics", "Ask Knowledge Base", "Create Task From Prompt", "Document Center", "Manage Knowledge Base", "Mail Merge"])

    with tabs[0]:
        tasks = task_service.as_frame(st.session_state.get("username", ""))
        if tasks.empty:
            st.info("No task data available.")
        else:
            status_counts = tasks["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            priority_counts = tasks["priority"].value_counts().reset_index()
            priority_counts.columns = ["priority", "count"]
            col1, col2 = st.columns(2)
            with col1:
                render_chart_container(status_counts, "status", "count", "Task Status Distribution", kind="pie")
            with col2:
                render_chart_container(priority_counts, "priority", "count", "Priority Distribution", kind="bar", color="priority")
            render_data_table(tasks, "Task analytics table", "task_analytics.xlsx")

    with tabs[1]:
        render_filter_panel("Knowledge workspace", "Ask policy and operational questions against indexed documents.")
        dept = st.text_input("Department Filter", value=st.session_state.get("user_dept", "ALL"))
        question = st.text_area("Question", placeholder="Summarize the latest KYC exception handling guidance.")
        if st.button("Ask Knowledge Base"):
            if not question.strip():
                st.error("Enter a question before submitting.")
            else:
                with st.spinner("Searching documents and preparing an answer..."):
                    result = qa_service.answer_question(question.strip(), dept_filter=dept.strip() or "ALL")
                st.markdown("### Answer")
                st.write(result["answer"])
                st.markdown("### Sources")
                st.write(result["sources"] or "No indexed sources found.")

    with tabs[2]:
        task_prompt = st.text_area("Task Instruction", placeholder="Follow up with branch 1234 on overdue audit compliance by Friday with high priority.")
        task_dept = st.text_input("Task Department", value=st.session_state.get("user_dept", "ALL"))
        if st.button("Create Task From Prompt"):
            if not task_prompt.strip():
                st.error("Enter a task instruction before submitting.")
            else:
                task = task_service.parse_nlp_task(task_prompt.strip(), st.session_state.get("username", ""), task_dept.strip() or "ALL")
                st.success("Task created successfully.")
                st.json(task.model_dump(mode="json"))

    with tabs[3]:
        st.subheader("Trilingual Office Note Generator")
        st.info("Generates notes with standard trilingual headers (English, Hindi, Tamil).")
        
        with st.form("office_note_form"):
            col1, col2 = st.columns(2)
            with col1:
                dept = st.text_input("Department", value=st.session_state.get("user_dept", "PLAN"))
                subject = st.text_input("Subject", placeholder="PAYMENT OF BILLS - FEB 2026")
            with col2:
                ref = st.text_input("Reference No (Optional)", placeholder="Leave blank for auto-gen")
                prepared_by = st.text_input("Prepared By", value=st.session_state.get("display_name") or st.session_state.get("username", "Staff User"))
            
            signatories = st.multiselect(
                "Additional Signatories",
                options=["Manager", "Senior Manager", "Chief Manager", "Asst. General Manager", "Deputy General Manager", "Regional Manager"],
                default=["Manager", "Senior Manager", "Chief Manager"]
            )
            
            intro = st.text_area("Introduction / Context", placeholder="Briefly describe the purpose of this note.")
            obs = st.text_area("Observations", placeholder="List technical or financial observations.")
            recs = st.text_area("Recommendations", placeholder="State the final recommendation for approval.")
            
            submitted = st.form_submit_button("Generate Trilingual Note")
            
            if submitted:
                html = doc_service.generate_office_note(
                    department=dept,
                    subject=subject,
                    intro_text=intro,
                    observations=obs,
                    recommendations=recs,
                    prepared_by=prepared_by,
                    ref_no=ref if ref else None,
                    signatories=signatories
                )
                st.session_state["preview_note"] = html
        
        if "preview_note" in st.session_state:
            st.markdown("### Preview")
            st.components.v1.html(st.session_state["preview_note"], height=500, scrolling=True)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Download HTML",
                    data=st.session_state["preview_note"],
                    file_name=f"Office_Note_{datetime.date.today().isoformat()}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col2:
                pdf_data = doc_service.generate_pdf_note(
                    department=dept,
                    subject=subject,
                    intro_text=intro,
                    observations=obs,
                    recommendations=recs,
                    prepared_by=prepared_by,
                    ref_no=ref if ref else None,
                    signatories=signatories
                )
                st.download_button(
                    "Download PDF (Official)",
                    data=pdf_data,
                    file_name=f"Office_Note_{datetime.date.today().isoformat()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
            )

        st.divider()
        st.subheader("Branch Anniversary Note")
        with st.form("anniversary_note_form"):
            col1, col2 = st.columns(2)
            with col1:
                br_name = st.text_input("Branch Name", placeholder="Dindigul Main")
                br_code = st.text_input("Branch SOL Code", placeholder="0001")
            with col2:
                f_date = st.text_input("Foundation Date", placeholder="01.01.1970")
                years = st.number_input("Anniversary Year", min_value=1, value=50)
            
            anniv_submitted = st.form_submit_button("Generate Anniversary Note")
            
            if anniv_submitted:
                html = doc_service.generate_anniversary_note(
                    branch_name=br_name,
                    branch_code=br_code,
                    foundation_date=f_date,
                    years=int(years),
                    prepared_by=st.session_state.get("display_name") or st.session_state.get("username", "Staff User")
                )
                st.session_state["preview_note"] = html

    with tabs[4]:
        uploaded_files = st.file_uploader(
            "Upload Knowledge Documents",
            type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
        )
        department = st.text_input("Document Department", value=st.session_state.get("user_dept", "ALL"))
        if st.button("Index Uploaded Documents"):
            if not uploaded_files:
                st.error("Upload at least one document before indexing.")
            else:
                records = indexing_service.index_uploaded_documents(uploaded_files, department=department, uploaded_by=st.session_state.get("username", "unknown"))
                st.success(f"Indexed {len(records)} document(s).")
                st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        indexed = [item.model_dump(mode="json") for item in indexing_service.list_documents()]
        if indexed:
            render_data_table(pd.DataFrame(indexed), "Indexed documents", "indexed_documents.xlsx")

    with tabs[5]:
        st.subheader("Bulk Mail Merge Engine")
        st.info("💡 **How it works:** Upload an Excel file with columns matching your template variables (e.g., {{NAME}}, {{ADDRESS}}).")
        
        col_t, col_d = st.columns(2)
        
        with col_t:
            st.markdown("#### 1. Define HTML Template")
            template_text = st.text_area("HTML Content", value="""
<div style="font-family: Arial; padding: 40px;">
    <h1>Notice to {{NAME}}</h1>
    <p>Dear {{NAME}},</p>
    <p>This is regarding your account with SOL <strong>{{BRANCH}}</strong>.</p>
    <p>Please visit the branch regarding {{SUBJECT}}.</p>
    <br>
    <p>Regional Manager,<br>Dindigul</p>
</div>
            """, height=300, key="mm_tpl")
            
        with col_d:
            st.markdown("#### 2. Upload Data Source")
            data_file = st.file_uploader("Upload Excel/CSV for Merge", type=["xlsx", "csv"], key="mm_file")
            if data_file:
                df = pd.read_excel(data_file) if data_file.name.endswith("xlsx") else pd.read_csv(data_file)
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 Process Bulk Merge"):
                    with st.spinner("Generating high-fidelity PDFs..."):
                        try:
                            pdfs = mm_service.process_merge(template_text, df)
                            st.success(f"Generated {len(pdfs)} documents successfully!")
                            st.download_button("Download All (Zipped)", data=b"placeholder", file_name="merged_docs.zip")
                        except Exception as e:
                            st.error(f"Merge failed: {str(e)}")
