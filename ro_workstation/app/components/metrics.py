import streamlit as st

def render_metrics(summary):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Open Tasks", summary["open"])
    col2.metric("Overdue", summary["overdue"])

    completion_rate = (
        (summary["open"] - summary["overdue"]) / summary["open"] * 100
        if summary["open"] else 0
    )

    col3.metric("Completion Health", f"{completion_rate:.1f}%")

    col4.metric("Total Tasks", len(summary["tasks"]))
