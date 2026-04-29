from datetime import date

import streamlit as st
from dotenv import load_dotenv

from modules.tasks.engine import get_tasks_for_user
from modules.ui.theme import inject_global_styles
from modules.utils.auth import require_login


st.set_page_config(page_title="RO Workstation", page_icon="🏦", layout="wide")
inject_global_styles()
load_dotenv()

if require_login():
    st.sidebar.title("🏦 RO Workstation")
    st.sidebar.caption("Offline-first regional office operations console")

    username = st.session_state.get("username", "")
    department = st.session_state.get("user_dept", "ALL")
    role = st.session_state.get("user_role", "RO_User")
    tasks = get_tasks_for_user(username)
    open_tasks = len([task for task in tasks if task.status == "OPEN"])
    overdue_tasks = len([task for task in tasks if task.status == "OPEN" and task.due_date and task.due_date < date.today()])

    badge = f"🔴 {open_tasks}" if open_tasks > 0 else "🟢 0"
    st.sidebar.markdown(f"**Open tasks**: {badge}")
    st.sidebar.markdown(f"**Department**: {department}")
    st.sidebar.markdown(f"**Role**: {role}")
    if overdue_tasks:
        st.sidebar.warning(f"{overdue_tasks} task(s) need immediate attention.")

    pg = st.navigation(
        {
            "Operations Hub": [
                st.Page("pages/home.py", title=f"Control Center ({badge})", icon="🎯"),
                st.Page("pages/crmd.py", title="CRMD Workspace", icon="📈"),
                st.Page("pages/fi.py", title="FI Workspace", icon="🤝"),
                st.Page("pages/visits.py", title="Visit Manager", icon="🚗"),
                st.Page("pages/comms.py", title="Staff Comms", icon="📢"),
                st.Page("pages/meetings.py", title="Meetings", icon="🗓️"),
                st.Page("pages/grievances.py", title="Grievances", icon="⚖️"),
            ],
            "Intelligence & Review": [
                st.Page("pages/research.py", title="AI Research", icon="🔍"),
                st.Page("pages/scorecard.py", title="Branch Scorecard", icon="📊"),
                st.Page("pages/calculators.py", title="Calculators", icon="🧮"),
            ],
            "Department Desks": [
                st.Page("pages/plan.py", title="Planning", icon="🧭"),
                st.Page("pages/arid.py", title="ARID", icon="🌾"),
                st.Page("pages/hrdd.py", title="HRDD", icon="👥"),
                st.Page("pages/gad.py", title="GAD", icon="🏛️"),
                st.Page("pages/com.py", title="Compliance", icon="✅"),
                st.Page("pages/law.py", title="Law", icon="📚"),
                st.Page("pages/ins.py", title="Inspection", icon="🧾"),
                st.Page("pages/mkt.py", title="Marketing", icon="📣"),
                st.Page("pages/rsk.py", title="Risk", icon="🛡️"),
                st.Page("pages/sme.py", title="MSME", icon="🏭"),
                st.Page("pages/ret.py", title="Retail", icon="🏠"),
                st.Page("pages/rcc.py", title="RCC", icon="💻"),
            ],
            "System Administration": [
                st.Page("pages/masters.py", title="Master Data", icon="🗃️"),
            ],
            "Governance": [
                st.Page("pages/vault.py", title="Document Vault", icon="🔒"),
                st.Page("pages/vendors.py", title="Vendor Register", icon="🏢"),
                st.Page("pages/profile.py", title="Profile & Settings", icon="⚙️"),
            ],
        }
    )
    pg.run()
