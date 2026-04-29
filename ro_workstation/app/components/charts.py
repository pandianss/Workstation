import streamlit as st
import plotly.express as px


def _apply_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font={"family": "Aptos, Segoe UI, sans-serif", "color": "#1d3128"},
        title={"font": {"size": 20, "color": "#1d3128"}},
        margin={"l": 10, "r": 10, "t": 52, "b": 10},
        legend={"bgcolor": "rgba(255,255,255,0)", "orientation": "h", "y": -0.15},
    )
    return fig


def render_status_chart(df):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.pie(
        df,
        names="status",
        title="Task Status Distribution",
        color="status",
        color_discrete_map={"OPEN": "#cb8f3d", "CLOSED": "#1f6b52"},
        hole=0.48,
    )

    _apply_chart_theme(fig)
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
        title="Priority Distribution",
        color="priority",
        color_discrete_sequence=["#114c39", "#1f6b52", "#4d8a73", "#cb8f3d"],
    )

    fig.update_layout(showlegend=False)
    _apply_chart_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_trend_chart(df):
    if df.empty or "due_date" not in df.columns:
        return

    trend = df.groupby("due_date").size().reset_index(name="count")

    fig = px.line(
        trend,
        x="due_date",
        y="count",
        title="Task Trend Over Time",
        markers=True,
    )

    fig.update_traces(line={"color": "#1f6b52", "width": 3}, marker={"size": 8, "color": "#cb8f3d"})
    _apply_chart_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
