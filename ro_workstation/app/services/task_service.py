from datetime import date
from modules.tasks.engine import get_tasks_for_user
import streamlit as st

def get_task_summary():
    username = st.session_state.get("username", "")
    tasks = get_tasks_for_user(username)

    open_tasks = [t for t in tasks if t.status == "OPEN"]
    overdue = [
        t for t in open_tasks
        if t.due_date and t.due_date < date.today()
    ]

    # Normalize tasks to a clean dictionary structure
    normalized_tasks = []
    for t in tasks:
        normalized_tasks.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date,
            "description": t.description,
            "dept": t.dept
        })

    return {
        "open": len(open_tasks),
        "overdue": len(overdue),
        "tasks": normalized_tasks
    }
