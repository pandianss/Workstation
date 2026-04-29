import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from mock_data import generators

from ..notes.generator import NoteGenerator
from ..utils.page_helpers import render_generation_result, render_page_header
from .theme import render_callout


EXTRA_DEPARTMENT_CONFIG = {
    "ARID": {
        "title": "Agriculture & Rural Infra Dev",
        "description": "Monitor agri credit, KCC renewals, and SHG linkages.",
        "loader": generators.get_arid_data,
        "metrics": [
            ("Agri Credit (Cr)", lambda k: f"Rs {k['Total Agri (Cr)']} Cr"),
            ("KCC Accounts", lambda k: f"{k['Total KCC']:,}"),
            ("SHG Linked", lambda k: f"{k['Total SHG']:,}"),
            ("Agri NPA %", lambda k: f"{k['Avg Agri NPA %']}%"),
        ],
        "analytics_columns": ["Agri Credit (Cr)"],
        "chart_mode": "single",
    },
    "COM": {
        "title": "Compliance",
        "description": "Track KYC/AML alerts, RBI observations, and compliance follow-up.",
        "loader": generators.get_com_data,
        "metrics": [
            ("Open Observations", lambda k: f"{k['Total Open Obs.']}"),
            ("KYC Exceptions", lambda k: f"{k['Total KYC Exceptions']:,}"),
            ("STRs Filed", lambda k: f"{k['Total STRs']}"),
            ("Compliance %", lambda k: f"{k['Avg Compliance %']}%"),
        ],
        "analytics_columns": ["Open Audit Obs.", "KYC Exceptions"],
        "chart_mode": "group",
    },
    "GAD": {
        "title": "General Administration",
        "description": "Manage premises, leases, fixed assets, and support services.",
        "loader": generators.get_gad_data,
        "metrics": [
            ("Total Area (sqft)", lambda k: f"{k['Total Area (sqft)']:,}"),
            ("Average Rent", lambda k: f"Rs {k['Avg Rent (Rs)']:,}"),
            ("Leases < 90 Days", lambda k: f"{k['Leases Expiring < 90 Days']}"),
            ("Security Staff", lambda k: f"{k['Total Security']}"),
        ],
        "analytics_columns": ["Monthly Rent (Rs)"],
        "chart_mode": "single",
    },
    "HRDD": {
        "title": "Human Resources",
        "description": "Manage staffing strength, vacancies, training, and officer movement.",
        "loader": generators.get_hrdd_data,
        "metrics": [
            ("Officers", lambda k: f"{k['Total Officers']}"),
            ("Clerks", lambda k: f"{k['Total Clerks']}"),
            ("Sub-staff", lambda k: f"{k['Total Sub-staff']}"),
            ("Vacancies", lambda k: f"{k['Total Vacancies']}"),
        ],
        "analytics_columns": ["Officers", "Clerks", "Sub-staff"],
        "chart_mode": "stack",
    },
    "INS": {
        "title": "Inspection",
        "description": "Track audit ratings, irregularities, and closure of inspection points.",
        "loader": generators.get_ins_data,
        "metrics": [
            ("Avg Rating", lambda k: f"{k['Avg Rating']}"),
            ("Critical Obs.", lambda k: f"{k['Total Critical']}"),
            ("Major Obs.", lambda k: f"{k['Total Major']}"),
            ("Irregularities", lambda k: f"{k['Total Irregularities']}"),
        ],
        "analytics_columns": ["Critical Obs.", "Major Obs."],
        "chart_mode": "stack",
    },
    "LAW": {
        "title": "Law Department",
        "description": "Monitor litigation, DRT matters, and legal recovery actions.",
        "loader": generators.get_law_data,
        "metrics": [
            ("Suit Cases", lambda k: f"{k['Total Suit Cases']}"),
            ("Amount Involved", lambda k: f"Rs {k['Total Amt (Cr)']} Cr"),
            ("DRT Cases", lambda k: f"{k['Total DRT']}"),
            ("Lok Adalat Settled", lambda k: f"{k['Lok Adalat Settled']}"),
        ],
        "analytics_columns": ["Suit Filed Cases", "DRT Cases"],
        "chart_mode": "group",
    },
    "MKT": {
        "title": "Marketing",
        "description": "Track campaign performance, lead generation, and cross-sell activity.",
        "loader": generators.get_mkt_data,
        "metrics": [
            ("New SA", lambda k: f"{k['Total New SA']:,}"),
            ("Cross Sell", lambda k: f"{k['Total Cross Sell']:,}"),
            ("Leads", lambda k: f"{k['Total Leads']:,}"),
            ("Conversion %", lambda k: f"{k['Avg Conv. %']}%"),
        ],
        "analytics_columns": ["New SA Accts (YTD)"],
        "chart_mode": "single",
    },
    "PLAN": {
        "title": "Planning Department",
        "description": "Review branch business, monitor RO expense context, and generate formatted office notes.",
        "loader": generators.get_plan_data,
        "metrics": [
            ("Total Deposits", lambda k: f"Rs {k['Total Deposits (Cr)']} Cr"),
            ("Total Advances", lambda k: f"Rs {k['Total Advances (Cr)']} Cr"),
            ("CASA %", lambda k: f"{k['Overall CASA %']}%"),
            ("CD Ratio", lambda k: f"{k['Overall CD Ratio %']}%"),
        ],
        "analytics_columns": ["Deposits (Cr)", "Advances (Cr)"],
        "chart_mode": "group",
        "special_note": True,
    },
    "RCC": {
        "title": "Regional Computer Centre",
        "description": "Monitor uptime, open IT tickets, and infra support needs.",
        "loader": generators.get_rcc_data,
        "metrics": [
            ("CBS Uptime %", lambda k: f"{k['Avg CBS Uptime %']}%"),
            ("ATM Uptime %", lambda k: f"{k['Avg ATM Uptime %']}%"),
            ("Open IT Tickets", lambda k: f"{k['Total Open Tickets']}"),
            ("Hardware Requests", lambda k: f"{k['Total HW Reqs']}"),
        ],
        "analytics_columns": ["CBS Uptime %", "ATM Uptime %"],
        "chart_mode": "group",
    },
    "RET": {
        "title": "Retail Department",
        "description": "Monitor housing, auto, and personal loan portfolio movement.",
        "loader": generators.get_ret_data,
        "metrics": [
            ("Home Loans", lambda k: f"Rs {k['Total HL (Cr)']} Cr"),
            ("Auto Loans", lambda k: f"Rs {k['Total AL (Cr)']} Cr"),
            ("Personal Loans", lambda k: f"Rs {k['Total PL (Cr)']} Cr"),
            ("Retail NPA %", lambda k: f"{k['Avg Retail NPA %']}%"),
        ],
        "analytics_columns": ["Home Loans (Cr)", "Auto Loans (Cr)", "Personal Loans (Cr)"],
        "chart_mode": "group",
    },
    "RSK": {
        "title": "Risk Management",
        "description": "Review operational and cyber risk signals across branches.",
        "loader": generators.get_rsk_data,
        "metrics": [
            ("Avg Risk Score", lambda k: f"{k['Avg Risk Score']}"),
            ("Frauds", lambda k: f"{k['Total Frauds']}"),
            ("Cyber Incidents", lambda k: f"{k['Cyber Incidents']}"),
            ("Cash Shortages", lambda k: f"{k['Total Cash Short']}"),
        ],
        "analytics_columns": ["Risk Score"],
        "chart_mode": "single",
    },
    "SME": {
        "title": "MSME Division",
        "description": "Track MSME credit, Mudra disbursement, and guarantee coverage.",
        "loader": generators.get_sme_data,
        "metrics": [
            ("MSME Credit", lambda k: f"Rs {k['Total MSME (Cr)']} Cr"),
            ("MUDRA", lambda k: f"Rs {k['Total MUDRA (L)']} L"),
            ("CGTMSE", lambda k: f"Rs {k['Total CGTMSE (Cr)']} Cr"),
            ("MSME NPA %", lambda k: f"{k['Avg MSME NPA %']}%"),
        ],
        "analytics_columns": ["MSME Credit (Cr)"],
        "chart_mode": "single",
    },
}


def _render_standard_note_tab(dept_code: str, user_department: str) -> None:
    template = st.selectbox(
        "Select Template",
        ["Standard Approval Note", "Review Note", "Compliance Update"],
        key=f"{dept_code}_template",
    )
    subject = st.text_input("Subject", key=f"{dept_code}_subject")
    key_data = st.text_area("Key Data Points", key=f"{dept_code}_data")
    if st.button("Generate Draft", key=f"{dept_code}_draft"):
        with st.spinner("Drafting note..."):
            draft = NoteGenerator().generate_note(template, subject, key_data, user_department)
            render_generation_result("Draft Note", draft, f"{dept_code.lower()}_draft_note.txt")


def _render_plan_special_tab() -> None:
    st.subheader("A4 Office Note Generator")
    template = st.selectbox("Select Template", ["Payment of Bills"], key="plan_html_template")
    raw_data = st.text_area(
        "Paste raw vendor / invoice details",
        height=150,
        value="Ref: RO/DGL/PLNG/2026-27/05/04. Date: 29.04.2026. Vendor: Dream Designers (VEN123). Period: April 2026. Items: 1. 20.04.2026, Sign boards, Rs 5000, 100/pc. Total Rs 5000. Utilised: Rs 38696.",
    )
    if st.button("Generate HTML Note", key="plan_generate_html"):
        with st.spinner("Extracting data and generating A4 note..."):
            html_content = NoteGenerator().generate_html_note(template, raw_data)
            st.success("Note generated successfully.")
            components.html(html_content, height=800, scrolling=True)


def render_extra_department_page(dept_code: str) -> None:
    config = EXTRA_DEPARTMENT_CONFIG[dept_code]
    user = render_page_header(
        config["title"],
        config["description"],
        allowed_departments=[dept_code],
    )
    kpis, branch_df = config["loader"]()

    for index, (label, formatter) in enumerate(config["metrics"]):
        if index % 4 == 0:
            metric_columns = st.columns(4)
        metric_columns[index % 4].metric(label, formatter(kpis))

    render_callout("Department snapshot", f"{config['title']} is available through the shared workspace shell.")

    tab_labels = ["Dashboard", "Note Generator", "Returns", "Analytics", "Circulars", "Drafts"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.subheader("Branch-wise View")
        st.dataframe(branch_df, use_container_width=True, hide_index=True)

    with tabs[1]:
        if config.get("special_note"):
            _render_plan_special_tab()
        else:
            _render_standard_note_tab(dept_code, user["department"])

    with tabs[2]:
        st.info("Return scheduling will appear here when department return rules are configured.")

    with tabs[3]:
        columns = config["analytics_columns"]
        if config["chart_mode"] == "single":
            fig = px.bar(branch_df, x="Branch", y=columns[0], title=f"{columns[0]} by Branch")
        else:
            fig = px.bar(branch_df, x="Branch", y=columns, title="Branch comparison", barmode=config["chart_mode"])
        st.plotly_chart(fig, use_container_width=True)

    with tabs[4]:
        st.info(f"Recent circulars relevant to {dept_code} will appear here.")

    with tabs[5]:
        st.caption("No saved drafts yet.")
