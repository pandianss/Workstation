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

    st.markdown(
        f"""
        <div class="glass-panel" style="margin-top: 1rem;">
            <div class="section-title"><strong>Focus snapshot</strong></div>
            <div class="section-kicker">A quick read on current workload quality and operational pressure.</div>
            <div class="mini-stat-grid">
                <div class="mini-stat">
                    <div class="mini-stat__label">Healthy backlog</div>
                    <div class="mini-stat__value">{max(summary["open"] - summary["overdue"], 0)}</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-stat__label">Risk share</div>
                    <div class="mini-stat__value">{((summary["overdue"] / summary["open"]) * 100 if summary["open"] else 0):.1f}%</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-stat__label">Action stance</div>
                    <div class="mini-stat__value">{"Stable" if summary["overdue"] == 0 else "Attention"}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
