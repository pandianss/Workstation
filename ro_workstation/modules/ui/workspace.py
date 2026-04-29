import plotly.express as px
import streamlit as st

from ..notes.generator import NoteGenerator
from ..returns.builder import render_return_form
from ..returns.scheduler import get_upcoming_returns
from ..utils.page_helpers import render_generation_result, render_page_header
from .mock_data import WORKSPACE_DATA
from .theme import render_callout


def render_department_workspace(dept_code: str) -> None:
    workspace = WORKSPACE_DATA[dept_code]
    user = render_page_header(
        workspace["title"],
        workspace["description"],
        allowed_departments=[dept_code],
    )
    returns = get_upcoming_returns(dept_code)

    for index, (label, value, delta) in enumerate(workspace["metrics"]):
        if index % 4 == 0:
            metric_columns = st.columns(4)
        metric_columns[index % 4].metric(label, value, delta)

    render_callout(
        "Department focus",
        " | ".join(workspace["focus_items"][:2]),
    )

    overview_tab, workbench_tab, analytics_tab, guidance_tab = st.tabs(
        ["Overview", "Workbench", "Analytics", "Guidance"]
    )

    with overview_tab:
        left, right = st.columns([1.6, 1])
        with left:
            st.subheader("Branch Snapshot")
            st.dataframe(workspace["branches"], use_container_width=True)
        with right:
            st.subheader("Upcoming Returns")
            if returns:
                for item in returns:
                    due_marker = item.get("due_day") or item.get("due_month_day", "Scheduled")
                    st.markdown(f"- **{item['name']}**")
                    st.caption(f"Due: {due_marker} | Format: {item.get('format', 'Standard')}")
            else:
                st.info("No configured returns found for this department.")

            st.subheader("Needs Attention")
            for item in workspace["focus_items"]:
                st.write(f"- {item}")

    with workbench_tab:
        left, right = st.columns([1.15, 0.85])
        with left:
            st.subheader("Draft Office Note")
            template = st.selectbox(
                "Template",
                workspace["note_templates"],
                key=f"{dept_code.lower()}_template",
            )
            subject = st.text_input("Subject", key=f"{dept_code.lower()}_subject")
            key_data = st.text_area("Key Data Points", key=f"{dept_code.lower()}_key_data")
            if st.button("Generate Note", key=f"{dept_code.lower()}_generate_note"):
                with st.spinner("Drafting note..."):
                    draft = NoteGenerator().generate_note(template, subject, key_data, user["department"])
                    render_generation_result("Draft Note", draft, f"{dept_code.lower()}_draft_note.txt")
        with right:
            st.subheader("Return Preparation")
            if returns:
                selected_return = st.selectbox(
                    "Select return",
                    [item["name"] for item in returns],
                    key=f"{dept_code.lower()}_return_select",
                )
                render_return_form(
                    selected_return,
                    ["Reporting period", "Prepared by", "Key observations", "Action required"],
                )
            else:
                st.info("No return templates are configured yet.")

    with analytics_tab:
        st.subheader("Trend View")
        chart_df = workspace["branches"]
        fig = px.bar(
            chart_df,
            x="Branch",
            y=workspace["analytics_y"],
            color=workspace["analytics_y"],
            color_continuous_scale="Tealgrn",
            title=f"{workspace['analytics_y']} by branch",
        )
        st.plotly_chart(fig, use_container_width=True)

        if "Active %" in chart_df.columns:
            secondary = px.line(chart_df, x="Branch", y="Active %", markers=True, title="Active % trend")
            st.plotly_chart(secondary, use_container_width=True)

    with guidance_tab:
        circular_col, draft_col = st.columns(2)
        with circular_col:
            st.subheader("Circulars & Guidance")
            for title, status in workspace["circulars"]:
                st.write(f"- {title}")
                st.caption(f"Status: {status}")
        with draft_col:
            st.subheader("Saved Drafts")
            for draft in workspace["drafts"]:
                st.write(f"- {draft}")
