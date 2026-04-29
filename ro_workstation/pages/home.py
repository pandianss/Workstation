from datetime import date, timedelta

import pandas as pd
import streamlit as st

from modules.returns.scheduler import get_upcoming_returns
from modules.tasks.engine import get_tasks_for_user, parse_nlp_task, update_task_status
from modules.utils.page_helpers import format_due_date, render_page_header
from modules.ui.theme import render_callout


def collect_returns(user_dept: str) -> list[dict]:
    departments = [user_dept] if user_dept not in {"", "ALL"} else ["CRMD", "FI"]
    items: list[dict] = []
    for dept in departments:
        for ret in get_upcoming_returns(dept):
            items.append(
                {
                    "Department": dept,
                    "Return": ret["name"],
                    "Due": ret.get("due_day") or ret.get("due_month_day", "Scheduled"),
                    "Format": ret.get("format", "Standard"),
                }
            )
    return items


user = render_page_header(
    "Regional Office Control Center",
    "Start from the work that needs attention now, move quickly into department workspaces, and keep returns, notes, and reviews in one place.",
)

tasks = get_tasks_for_user(user["username"])
open_tasks = [task for task in tasks if task.status == "OPEN"]
overdue_tasks = [task for task in open_tasks if task.due_date and task.due_date < date.today()]
due_soon_tasks = [
    task for task in open_tasks if task.due_date and date.today() <= task.due_date <= date.today() + timedelta(days=3)
]
returns = collect_returns(user["department"])

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Open Tasks", len(open_tasks))
metric_2.metric("Overdue", len(overdue_tasks))
metric_3.metric("Due in 3 Days", len(due_soon_tasks))
metric_4.metric("Configured Returns", len(returns))

if overdue_tasks:
    render_callout(
        "Immediate attention",
        " | ".join(f"{task.title} ({format_due_date(task.due_date)})" for task in overdue_tasks[:3]),
    )

launch_col, add_col = st.columns([1.35, 1])
with launch_col:
    st.subheader("Quick Launch")
    nav_1, nav_2, nav_3 = st.columns(3)
    with nav_1:
        st.page_link("pages/crmd.py", label="Open CRMD Workspace", icon="📈")
        st.page_link("pages/research.py", label="Search Research", icon="🔍")
    with nav_2:
        st.page_link("pages/fi.py", label="Open FI Workspace", icon="🤝")
        st.page_link("pages/vault.py", label="Open Vault", icon="🔒")
    with nav_3:
        st.page_link("pages/meetings.py", label="Prepare Meeting", icon="🗓️")
        st.page_link("pages/profile.py", label="Handover & Settings", icon="⚙️")

with add_col:
    st.subheader("Quick Add Task")
    with st.form("quick_add_form", clear_on_submit=True):
        nl_input = st.text_input("Capture a task from a call, visit, or meeting")
        if st.form_submit_button("Add Task"):
            if nl_input.strip():
                parse_nlp_task(nl_input, user["username"], user["department"])
                st.success("Task added to your queue.")
                st.rerun()
            else:
                st.warning("Enter a task description first.")

focus_col, return_col = st.columns([1.5, 1])
with focus_col:
    st.subheader("Work Queue")
    if not open_tasks:
        st.info("No open tasks right now.")
    else:
        queue_filter = st.radio("Show", ["Priority first", "Due soon", "All open"], horizontal=True)
        if queue_filter == "Due soon":
            visible_tasks = due_soon_tasks or open_tasks
        elif queue_filter == "All open":
            visible_tasks = open_tasks
        else:
            visible_tasks = sorted(open_tasks, key=lambda task: (task.priority, task.due_date or date.max))

        for task in visible_tasks[:10]:
            row_1, row_2, row_3, row_4 = st.columns([1, 4, 2, 1.4])
            row_1.markdown(f"**{task.priority}**")
            row_2.write(task.title)
            row_3.caption(f"Due: {format_due_date(task.due_date)}")
            if row_4.button("Done", key=f"done_{task.id}"):
                update_task_status(task.id, "DONE")
                st.rerun()

with return_col:
    st.subheader("Return Calendar")
    if returns:
        st.dataframe(pd.DataFrame(returns), use_container_width=True, hide_index=True)
    else:
        st.info("No return schedule available for this role.")

st.subheader("Completed Recently")
completed = [task for task in tasks if task.status == "DONE"][:5]
if completed:
    completed_df = pd.DataFrame(
        {
            "Task": [task.title for task in completed],
            "Priority": [task.priority for task in completed],
            "Due": [format_due_date(task.due_date) for task in completed],
        }
    )
    st.dataframe(completed_df, use_container_width=True, hide_index=True)
else:
    st.caption("Closed tasks will start showing here as you work through the queue.")
