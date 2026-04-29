import pandas as pd
from modules.tasks.engine import get_tasks_for_user
import streamlit as st

def get_intelligence_data(filters):
    username = st.session_state.get("username", "")
    tasks = get_tasks_for_user(username)

    # Normalize tasks to a clean dictionary structure to avoid SQLAlchemy __dict__ issues
    normalized_tasks = []
    for t in tasks:
        normalized_tasks.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date,
            "created_at": getattr(t, "created_at", None),
            "dept": t.dept
        })

    df = pd.DataFrame(normalized_tasks)

    if df.empty:
        return df

    # Apply filters
    if filters["status"] != "All":
        df = df[df["status"] == filters["status"]]

    if filters["priority"] != "All":
        df = df[df["priority"] == filters["priority"]]
        
    if filters.get("search"):
        df = df[df.apply(
            lambda row: filters["search"].lower() in str(row).lower(),
            axis=1
        )]

    return df
