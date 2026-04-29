import streamlit as st
import plotly.express as px

def render_status_chart(df):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.pie(
        df,
        names="status",
        title="Task Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_priority_chart(df):
    if df.empty:
        return

    # Count frequencies for bar chart
    priority_counts = df["priority"].value_counts().reset_index()
    priority_counts.columns = ["priority", "count"]

    fig = px.bar(
        priority_counts,
        x="priority",
        y="count",
        title="Priority Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_trend_chart(df):
    if df.empty or "due_date" not in df.columns:
        return

    trend = df.groupby("due_date").size().reset_index(name="count")

    fig = px.line(
        trend,
        x="due_date",
        y="count",
        title="Task Trend Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)
