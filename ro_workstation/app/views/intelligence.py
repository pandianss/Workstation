import streamlit as st
from app.services.intelligence_service import get_intelligence_data
from app.services.mis_service import load_mis_data
from app.services.knowledge_service import (
    index_uploaded_documents,
    list_indexed_documents,
    SUPPORTED_EXTENSIONS,
)
from app.components.filters import render_task_filters
from app.components.charts import (
    render_status_chart,
    render_priority_chart,
    render_trend_chart,
)
from modules.knowledge.qa import answer_question
from modules.tasks.engine import parse_nlp_task


def render_intelligence():
    st.markdown("## Intelligence")
    st.markdown(
        """
        <div class="glass-panel">
            <div class="section-title"><strong>Analysis and automation</strong></div>
            <div class="section-kicker">
                Explore patterns, ask questions against indexed knowledge, and turn instructions into action-ready tasks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    analytics_tab, ask_tab, task_tab, knowledge_tab, perf_tab = st.tabs(
        ["Task Analytics", "Ask Knowledge Base", "Create Task From Prompt", "Manage Knowledge Base", "Performance Insights"]
    )

    with analytics_tab:
        filters = render_task_filters()
        data = get_intelligence_data(filters)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            render_status_chart(data)

        with col2:
            render_priority_chart(data)

        st.markdown("### Trends")
        render_trend_chart(data)

    user_dept = st.session_state.get("user_dept", "ALL")

    with ask_tab:
        indexed_df = list_indexed_documents()
        st.caption("Ask a natural-language question against the indexed knowledge base.")
        if indexed_df.empty:
            st.warning("No documents are indexed yet. Use the Manage Knowledge Base tab first.")

        dept_filter = st.text_input("Department Filter", value=user_dept, key="kb_dept_filter")
        query = st.text_area(
            "Question",
            placeholder="Example: Summarize the latest KYC exception handling guidance.",
        )

        if st.button("Ask", key="ask_knowledge_btn"):
            if not query.strip():
                st.error("Enter a question before submitting.")
            else:
                with st.spinner("Searching documents and preparing an answer..."):
                    result = answer_question(query.strip(), dept_filter=dept_filter.strip() or "ALL")

                st.markdown("### Answer")
                st.write(result["answer"])

                st.markdown("### Sources")
                if result["sources"]:
                    for idx, source in enumerate(result["sources"], start=1):
                        st.write(f"[{idx}] {source}")
                else:
                    st.info("No indexed sources were found for this prompt.")

    with task_tab:
        st.caption("Turn a prompt into a task with normalized priority and due date.")
        task_prompt = st.text_area(
            "Task Instruction",
            placeholder="Example: Follow up with branch 1234 on overdue audit compliance by Friday with high priority.",
        )
        task_dept = st.text_input("Task Department", value=user_dept, key="task_dept_filter")

        if st.button("Create Task", key="create_task_from_prompt_btn"):
            if not task_prompt.strip():
                st.error("Enter a task instruction before submitting.")
            else:
                with st.spinner("Parsing prompt and creating task..."):
                    task = parse_nlp_task(
                        task_prompt.strip(),
                        st.session_state.get("username", ""),
                        task_dept.strip() or "ALL",
                    )

                st.success("Task created successfully.")
                st.json(
                    {
                        "id": task.id,
                        "title": task.title,
                        "priority": task.priority,
                        "due_date": str(task.due_date),
                        "dept": task.dept,
                        "status": task.status,
                    }
                )

    with knowledge_tab:
        st.caption(
            f"Upload and index source documents before querying them. Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )
        department = st.text_input("Document Department", value=user_dept, key="knowledge_dept")
        uploaded_files = st.file_uploader(
            "Upload Knowledge Documents",
            type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
        )

        if st.button("Index Uploaded Documents", key="index_docs_btn"):
            if not uploaded_files:
                st.error("Upload at least one document before indexing.")
            else:
                with st.spinner("Saving files and indexing document chunks..."):
                    indexed_records = index_uploaded_documents(
                        uploaded_files,
                        department=department.strip() or "ALL",
                        uploaded_by=st.session_state.get("username", "unknown"),
                    )

                st.success(f"Indexed {len(indexed_records)} document(s).")
                st.dataframe(indexed_records, use_container_width=True, hide_index=True)

        st.markdown("### Indexed Documents")
        indexed_df = list_indexed_documents()
        if indexed_df.empty:
            st.info("No documents indexed yet.")
        else:
            st.dataframe(indexed_df, use_container_width=True, hide_index=True)

    with perf_tab:
        st.markdown("### AI Performance Advisory")
        st.caption("Automated analysis of Regional performance trends using the latest MIS data.")
        
        mis_df = load_mis_data()
        if mis_df.empty:
            st.warning("No MIS data available for analysis.")
        else:
            # Get latest date
            latest_date = mis_df['DATE'].max()
            current_df = mis_df[mis_df['DATE'] == latest_date]
            
            # Aggregate for the region
            reg_total = current_df[current_df['SOL'] == 3933]
            if reg_total.empty:
                reg_total = current_df # fallback
            
            adv = reg_total['Total Advances'].sum()
            dep = reg_total['Total Deposits'].sum()
            npa = reg_total['NPA'].sum() if 'NPA' in reg_total.columns else 0
            
            # Prepare context for LLM
            perf_context = f"Latest Data Date: {latest_date}\nTotal Advances: {adv:.2f} Cr\nTotal Deposits: {dep:.2f} Cr\nTotal NPA: {npa:.2f} Cr\nCD Ratio: {(adv/dep*100):.2f}%"
            
            if st.button("Generate Performance Advisory"):
                from modules.llm.client import LLMClient
                llm = LLMClient()
                with st.spinner("Analyzing performance data..."):
                    prompt = f"Based on the following bank performance data, provide 3 key strategic recommendations for the Regional Manager:\n\n{perf_context}"
                    advisory = llm.generate(prompt, "You are a Senior Banking Operations Consultant.")
                
                st.markdown("#### Strategic Recommendations")
                st.write(advisory)
                
                st.info("Note: This advisory is generated based on current raw metrics and is intended for decision support.")

