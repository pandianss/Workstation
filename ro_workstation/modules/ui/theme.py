import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(27, 89, 96, 0.15), transparent 35%),
                radial-gradient(circle at top left, rgba(22, 49, 63, 0.12), transparent 30%),
                linear-gradient(180deg, #f0f5f3 0%, #e8eef2 100%);
            color: #16313f;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #122833 0%, #174245 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        [data-testid="stSidebar"] * {
            color: #e2ede8;
        }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 20px;
            padding: 16px 20px;
            box-shadow: 0 10px 30px rgba(22, 49, 63, 0.05), inset 0 2px 0 rgba(255, 255, 255, 0.8);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 14px 35px rgba(22, 49, 63, 0.08), inset 0 2px 0 rgba(255, 255, 255, 1);
        }
        .ro-hero {
            padding: 1.5rem 1.8rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #16313f 0%, #1b5960 50%, #2f7f70 100%);
            color: #ffffff;
            margin-bottom: 1.2rem;
            box-shadow: 0 20px 50px rgba(22, 49, 63, 0.2);
            position: relative;
            overflow: hidden;
        }
        .ro-hero::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at top right, rgba(255,255,255,0.1), transparent 60%);
            pointer-events: none;
        }
        .ro-hero h1, .ro-hero h2, .ro-hero h3, .ro-hero p {
            color: inherit;
            margin: 0;
            position: relative;
            z-index: 1;
        }
        .ro-hero h2 {
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .ro-eyebrow {
            display: inline-block;
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #a7dcd0;
            position: relative;
            z-index: 1;
        }
        .ro-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
            position: relative;
            z-index: 1;
        }
        .ro-chip {
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .ro-chip:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        .ro-panel {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            border-radius: 20px;
            padding: 1.25rem 1.25rem 0.5rem 1.25rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 12px 35px rgba(22, 49, 63, 0.04), inset 0 2px 0 rgba(255, 255, 255, 0.7);
            transition: all 0.3s ease;
        }
        .ro-panel:hover {
            box-shadow: 0 16px 40px rgba(22, 49, 63, 0.06), inset 0 2px 0 rgba(255, 255, 255, 0.9);
        }
        .ro-panel h3 {
            margin-top: 0;
            font-weight: 600;
            color: #122833;
        }
        .ro-callout {
            background: linear-gradient(135deg, rgba(47, 127, 112, 0.08), rgba(33, 97, 103, 0.12));
            border-left: 4px solid #2f7f70;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        }
        .ro-list {
            margin: 0.2rem 0 0.8rem 0;
            padding-left: 1.2rem;
        }
        .ro-list li {
            margin-bottom: 0.5rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.6rem;
            padding: 0.2rem;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 999px;
            padding: 0.5rem 1rem;
            border: 1px solid rgba(255, 255, 255, 0.4);
            transition: all 0.2s ease;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.8);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #122833 0%, #1b5960 100%) !important;
            color: #ffffff !important;
            border: none;
            box-shadow: 0 4px 12px rgba(22, 49, 63, 0.2);
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #1b5960 0%, #2f7f70 100%);
            color: white;
            font-weight: 600;
            padding: 0.5rem 1.2rem;
            box-shadow: 0 6px 16px rgba(27, 89, 96, 0.2);
            transition: all 0.2s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(27, 89, 96, 0.3);
            color: white;
        }
        .stButton > button:active, .stDownloadButton > button:active {
            transform: translateY(1px);
            box-shadow: 0 4px 10px rgba(27, 89, 96, 0.2);
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stNumberInput input {
            border-radius: 12px !important;
            border: 1px solid rgba(22, 49, 63, 0.1) !important;
            background: rgba(255, 255, 255, 0.9) !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"] > div:focus {
            border-color: #2f7f70 !important;
            box-shadow: 0 0 0 2px rgba(47, 127, 112, 0.2) !important;
        }
        .ro-muted {
            color: #64818c;
            font-size: 0.9rem;
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

