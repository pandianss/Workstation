import plotly.express as px
import streamlit as st
import yaml

from modules.ui.mock_data import scorecard_df
from modules.utils.page_helpers import render_page_header
from modules.utils.paths import project_path


@st.cache_data
def load_weights():
    try:
        with project_path("config", "scorecard.yaml").open(encoding="utf-8") as file:
            return yaml.safe_load(file).get("kpi_weights", {})
    except Exception:
        return {}


render_page_header(
    "Branch Scorecard",
    "Compare branches against weighted KPIs and identify where review attention should shift next.",
)

weights = load_weights()
df = scorecard_df()

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Top Score", f"{df['Score'].max():.0f}")
metric_2.metric("Lowest Score", f"{df['Score'].min():.0f}")
metric_3.metric("Average Score", f"{df['Score'].mean():.1f}")

left, right = st.columns([1.5, 1])
with left:
    st.subheader("Ranked Branch View")
    st.dataframe(df.sort_values(by="Score", ascending=False), use_container_width=True, hide_index=True)
with right:
    st.subheader("Configured Weights")
    if weights:
        for kpi, weight in weights.items():
            st.write(f"- {kpi.replace('_', ' ').title()}: {weight * 100:.0f}%")
    else:
        st.info("Weight configuration not found.")

st.subheader("Comparative Trend")
fig = px.bar(df, x="Branch", y="Score", color="Score", color_continuous_scale="Tealgrn")
st.plotly_chart(fig, use_container_width=True)
