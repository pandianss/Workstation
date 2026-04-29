import plotly.express as px
import plotly.graph_objects as go

def plot_branch_kpi_bar(df, branch_col, kpi_col, title):
    fig = px.bar(df, x=branch_col, y=kpi_col, title=title, color=kpi_col, color_continuous_scale="Blues")
    fig.update_layout(xaxis_title="Branch", yaxis_title=kpi_col)
    return fig

def plot_kpi_gauge(value, target, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, target * 1.2]},
            'steps': [
                {'range': [0, target * 0.8], 'color': "lightgray"},
                {'range': [target * 0.8, target], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target}}))
    return fig
