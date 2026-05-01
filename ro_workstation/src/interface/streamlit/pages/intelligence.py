from __future__ import annotations

import datetime
import pandas as pd
import streamlit as st

from src.application.services.document_service import DocumentService
from src.application.services.task_service import TaskService
from src.application.services.mail_merge_service import MailMergeService
from src.application.services.advances_service import AdvancesService
from src.application.services.circular_service import CircularService
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

def get_doc_service():
    return DocumentService()

@st.cache_resource
def get_mail_merge_service():
    return MailMergeService()

def get_advances_service():
    return AdvancesService()

def get_circular_service():
    return CircularService()


def render() -> None:
    task_service = get_task_service()
    indexing_service = get_indexing_service()
    qa_service = get_qa_service()
    search_service = get_search_service()
    doc_service = get_doc_service()
    mm_service = get_mail_merge_service()
    adv_service = get_advances_service()
    circ_service = get_circular_service()

    render_action_bar("Intelligence & Documents", ["Analytics", "Office Notes", "Circulars", "Knowledge"])
    tabs = st.tabs(["Task Analytics", "Advances Analytics", "Official Circulars", "Ask Knowledge", "Document Generator", "Manage Knowledge", "Mail Merge"])

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

        st.divider()
        st.markdown("#### AI Task Creation")
        with st.expander("Generate Task from Natural Language", expanded=False):
            task_prompt = st.text_area("Task Instruction", placeholder="Follow up with branch 1234 on overdue audit compliance by Friday with high priority.")
            task_dept = st.text_input("Task Department", value=st.session_state.get("user_dept", "ALL"), key="nlp_task_dept")
            if st.button("Create Task"):
                if not task_prompt.strip():
                    st.error("Enter a task instruction.")
                else:
                    task = task_service.parse_nlp_task(task_prompt.strip(), st.session_state.get("username", ""), task_dept.strip() or "ALL")
                    st.success("Task created successfully.")
                    st.json(task.model_dump(mode="json"))

    with tabs[1]:
        st.subheader("🏦 Advances Portfolio Analytics")
        st.info("Incorporate logic from high-fidelity banking performance samples. Upload Advances file for 3-level classification and risk analysis.")
        
        uploaded_adv = st.file_uploader("Upload Advances Excel", type=["xlsx", "xls"], key="adv_upload")
        if uploaded_adv:
            with st.spinner("Processing advanced classification..."):
                df = adv_service.process_excel(uploaded_adv)
                stats = adv_service.get_summary_stats(df)
            
            # Metric Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Accounts", f"{stats['total_count']:,}")
            m2.metric("Total Balance", f"₹{stats['total_balance_cr']:.2f} Cr")
            m3.metric("NPA Amount", f"₹{stats.get('risk_summary', {}).get('NPA', {}).get('sum', 0):.2f} Cr")
            m4.metric("SMA-2 Amount", f"₹{stats.get('risk_summary', {}).get('SMA-2', {}).get('sum', 0):.2f} Cr")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Portfolio by Category (L1)")
                cat_df = pd.DataFrame(list(stats['by_category'].items()), columns=['Category', 'Balance (Cr)'])
                st.bar_chart(cat_df.set_index('Category'))
            
            with col_b:
                st.markdown("#### Asset Quality Mix")
                risk_df = pd.DataFrame([{'Risk': k, 'Balance': v['sum']} for k, v in stats['risk_summary'].items()])
                st.bar_chart(risk_df.set_index('Risk'))

            st.markdown("#### Detailed Sector Analysis (L2)")
            sector_df = pd.DataFrame([{'Sector': k, 'Count': v['count'], 'Balance (Cr)': v['sum']} for k, v in stats['by_sector'].items()])
            st.dataframe(sector_df, use_container_width=True, hide_index=True)
            
            with st.expander("View Raw Enriched Data"):
                st.dataframe(df, use_container_width=True)

    with tabs[2]:
        st.subheader("📜 Official Circular Management")
        st.info("Draft and manage regional circulars with auto-incrementing reference numbers.")
        
        with st.form("circular_form"):
            c1, c2 = st.columns(2)
            with c1:
                circ_dept = st.text_input("Department Code", value=st.session_state.get("user_dept", "PLAN"))
                circ_subject = st.text_input("Circular Subject")
            with c2:
                region_code = "DGL" # Default for Dindigul
                ref_no = circ_service.generate_ref_no(region_code, circ_dept)
                st.text_input("Reference Number", value=ref_no, disabled=True)
                issuance_date = st.date_input("Issuance Date", value=datetime.date.today())
            
            recipients = st.radio("Recipients", ["All Branches", "Specific Selection"], horizontal=True)
            circ_body = st.text_area("Circular Body Content", height=300)
            circ_conclusion = st.text_input("Conclusion / Instructions", value="Please acknowledge receipt and ensure compliance.")
            
            circ_submitted = st.form_submit_button("Save Circular Draft")
            
            if circ_submitted:
                circular = {
                    "ref_no": ref_no,
                    "subject": circ_subject,
                    "dept": circ_dept,
                    "date": issuance_date.isoformat(),
                    "recipients": recipients,
                    "body": circ_body,
                    "conclusion": circ_conclusion,
                    "author": st.session_state.get("username", "Staff")
                }
                circ_service.save_circular(circular)
                st.success(f"Circular {ref_no} saved successfully!")

        st.markdown("#### Recent Circulars")
        all_circs = circ_service.get_all()
        if all_circs:
            for i, c in enumerate(all_circs):
                with st.container(border=True):
                    col_info, col_action = st.columns([4, 1])
                    with col_info:
                        # Check if "NEW" (within 7 days)
                        is_new = False
                        try:
                            # Handle both ISO format and YYYY-MM-DD
                            c_date_str = c.get('date', '')
                            if 'T' in c_date_str:
                                p_date = datetime.datetime.fromisoformat(c_date_str)
                            else:
                                p_date = datetime.datetime.strptime(c_date_str, "%Y-%m-%d")
                            
                            if (datetime.datetime.now() - p_date).days <= 7:
                                is_new = True
                        except Exception:
                            pass
                        
                        subject = c.get("subject") or c.get("title") or "Untitled Circular"
                        ref = c.get("ref_no") or c.get("number") or "N/A"
                        date_str = c.get("date", "N/A")
                        
                        if is_new:
                            st.markdown(f"### 🆕 {subject}")
                        else:
                            st.markdown(f"### {subject}")
                        
                        st.markdown(f"**Ref:** `{ref}` | **Date:** {date_str} | **Author:** {c.get('author', 'Regional Office')}")
                    
                    with col_action:
                        st.write("") # Spacer
                        pdf_bytes = doc_service.generate_circular_pdf(c)
                        st.download_button(
                            "📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Circular_{ref.replace('/', '_')}.pdf",
                            mime="application/pdf",
                            key=f"dl_circ_{i}",
                            use_container_width=True
                        )
        else:
            st.info("No published circulars found.")

    with tabs[3]:
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


    with tabs[4]:
        st.subheader("Trilingual Office Note Generator")
        st.info("Generates notes with standard trilingual headers (English, Hindi, Tamil).")
        
        st.markdown("#### AI-Assisted Drafting")
        with st.expander("Generate note content from a brief description", expanded=False):
            ai_brief = st.text_area(
                "Brief / Key Points",
                placeholder=(
                    "e.g., Bills worth ₹4.2L received for Feb 2026 from vendors ABC and XYZ. "
                    "Payments pending approval. Budgetary provision exists under GAD head."
                ),
                key="ai_brief_input",
                height=100,
            )
            ai_dept_for_draft = st.text_input(
                "Department",
                value=st.session_state.get("user_dept", "PLAN"),
                key="ai_draft_dept",
            )
            ai_subject_for_draft = st.text_input(
                "Subject",
                placeholder="PAYMENT OF BILLS — FEB 2026",
                key="ai_draft_subject",
            )
            if st.button("Generate Draft with AI", key="ai_draft_btn"):
                if not ai_brief.strip():
                    st.error("Enter a brief description first.")
                else:
                    with st.spinner("Drafting note content using local AI..."):
                        try:
                            from src.infrastructure.llm.client import LLMClient
                            from src.core.config.config_loader import load_yaml

                            _llm = LLMClient()
                            _prompts = load_yaml("src/config/prompts.yaml")
                            _dept_sys = (
                                _prompts.get(ai_dept_for_draft.upper(), {}).get("system", "")
                            )
                            drafted = doc_service.draft_office_note_content(
                                subject=ai_subject_for_draft.strip() or "Office Note",
                                department=ai_dept_for_draft.strip(),
                                brief=ai_brief.strip(),
                                llm=_llm,
                                dept_system_prompt=_dept_sys,
                            )
                            st.session_state["ai_drafted_intro"] = drafted.get("introduction", "")
                            st.session_state["ai_drafted_obs"] = drafted.get("observations", "")
                            st.session_state["ai_drafted_recs"] = drafted.get("recommendations", "")
                            st.success("Draft generated — review and edit below before generating the note.")
                        except Exception as e:
                            st.error(f"AI drafting failed: {e}")

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
            
            intro = st.text_area(
                "Introduction / Context",
                value=st.session_state.pop("ai_drafted_intro", ""),
                placeholder="Briefly describe the purpose of this note.",
            )
            obs = st.text_area(
                "Observations",
                value=st.session_state.pop("ai_drafted_obs", ""),
                placeholder="List technical or financial observations.",
            )
            recs = st.text_area(
                "Recommendations",
                value=st.session_state.pop("ai_drafted_recs", ""),
                placeholder="State the final recommendation for approval.",
            )
            
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

    with tabs[5]:
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

    with tabs[6]:
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
                            zip_bytes = mm_service.process_merge_zip(template_text, df)
                            st.download_button(
                                "Download All (Zipped)",
                                data=zip_bytes,
                                file_name="merged_documents.zip",
                                mime="application/zip",
                                use_container_width=True,
                            )
                        except Exception as e:
                            st.error(f"Merge failed: {str(e)}")
