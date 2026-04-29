import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(18, 121, 88, 0.10), transparent 28%),
                radial-gradient(circle at top left, rgba(18, 55, 88, 0.10), transparent 24%),
                linear-gradient(180deg, #f4f8f6 0%, #eef3f7 100%);
            color: #16313f;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #16313f 0%, #1e4b4d 100%);
        }
        [data-testid="stSidebar"] * {
            color: #f2f7f4;
        }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(22, 49, 63, 0.08);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 10px 30px rgba(22, 49, 63, 0.08);
        }
        .ro-hero {
            padding: 1.2rem 1.25rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #16313f 0%, #20595d 58%, #2f7f70 100%);
            color: #f6fbf8;
            margin-bottom: 1rem;
            box-shadow: 0 18px 45px rgba(22, 49, 63, 0.18);
        }
        .ro-hero h1, .ro-hero h2, .ro-hero h3, .ro-hero p {
            color: inherit;
            margin: 0;
        }
        .ro-eyebrow {
            display: inline-block;
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 0.45rem;
            color: #c9efe5;
        }
        .ro-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.85rem;
        }
        .ro-chip {
            padding: 0.38rem 0.7rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.16);
            font-size: 0.82rem;
        }
        .ro-panel {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(22, 49, 63, 0.08);
            border-radius: 20px;
            padding: 1rem 1rem 0.4rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(22, 49, 63, 0.06);
        }
        .ro-panel h3 {
            margin-top: 0;
        }
        .ro-callout {
            background: linear-gradient(135deg, rgba(33, 97, 103, 0.12), rgba(47, 127, 112, 0.16));
            border-left: 4px solid #2f7f70;
            padding: 0.9rem 1rem;
            border-radius: 14px;
            margin: 0.8rem 0 1rem 0;
        }
        .ro-list {
            margin: 0.2rem 0 0.6rem 0;
            padding-left: 1rem;
        }
        .ro-list li {
            margin-bottom: 0.45rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.6);
            border-radius: 999px;
            padding: 0.4rem 0.9rem;
            border: 1px solid rgba(22, 49, 63, 0.08);
        }
        .stTabs [aria-selected="true"] {
            background: #16313f !important;
            color: #f5faf7 !important;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #1b5960 0%, #2f7f70 100%);
            color: white;
            font-weight: 600;
            box-shadow: 0 8px 20px rgba(27, 89, 96, 0.18);
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stNumberInput input {
            border-radius: 12px !important;
        }
        .ro-muted {
            color: #56707a;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, description: str, eyebrow: str = "Regional Office Workstation", chips: list[str] | None = None) -> None:
    chip_html = ""
    if chips:
        chip_html = '<div class="ro-chip-row">' + "".join(f'<span class="ro-chip">{chip}</span>' for chip in chips) + "</div>"
    st.markdown(
        f"""
        <div class="ro-hero">
            <div class="ro-eyebrow">{eyebrow}</div>
            <h2>{title}</h2>
            <p style="margin-top:0.45rem; line-height:1.55;">{description}</p>
            {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel(title: str, description: str | None = None) -> None:
    subtitle = f'<p class="ro-muted">{description}</p>' if description else ""
    st.markdown(f'<div class="ro-panel"><h3>{title}</h3>{subtitle}</div>', unsafe_allow_html=True)


def render_callout(title: str, body: str) -> None:
    st.markdown(f'<div class="ro-callout"><strong>{title}</strong><br>{body}</div>', unsafe_allow_html=True)

