from __future__ import annotations

import pandas as pd


WORKSPACE_DATA = {
    "CRMD": {
        "title": "Credit Monitoring & Recovery",
        "description": "Watch stressed assets, manage recovery actions, and prepare credit monitoring submissions.",
        "metrics": [
            ("Gross NPA %", "5.2%", "-0.1%"),
            ("Net NPA %", "1.8%", "-0.05%"),
            ("SMA-2 Accounts", "142", "+12"),
            ("Recovery vs Target", "82%", "+4%"),
        ],
        "branches": pd.DataFrame(
            {
                "Branch": ["Mumbai Main", "Andheri", "Thane", "Borivali"],
                "Gross NPA (Cr)": [120, 85, 45, 30],
                "SMA-2 (Cr)": [15, 20, 5, 12],
                "Action Owner": ["CRMD Desk", "Zone Recovery", "Field Officer", "Branch Head"],
            }
        ),
        "note_templates": ["NPA Recovery Action (SARFAESI)", "IRAC Downgrade Note", "OTS Proposal"],
        "focus_items": [
            "Three SMA-2 accounts crossed the 25-day mark and need field follow-up.",
            "OTS proposal for XYZ Corp is awaiting revised branch viability inputs.",
            "Weekly flash report should reflect fresh slippages from Mumbai Main and Andheri.",
        ],
        "circulars": [
            ("RBI Master Circular on IRAC Norms", "Aligned"),
            ("HO OTS Scheme Guidelines", "Action pending"),
        ],
        "drafts": ["OTS Proposal - XYZ Corp", "SARFAESI review note - Thane cluster"],
        "analytics_y": "Gross NPA (Cr)",
    },
    "FI": {
        "title": "Financial Inclusion",
        "description": "Track outreach performance, inclusion coverage, and follow-up on FI returns.",
        "metrics": [
            ("PMJDY Accounts", "1,24,500", "+1200"),
            ("Zero Balance %", "12%", "-2%"),
            ("BC Outlet Count", "45/50", "+1"),
            ("Aadhaar Seeding", "88%", "+1.5%"),
        ],
        "branches": pd.DataFrame(
            {
                "Branch": ["Pune Main", "Shivaji Nagar", "Kothrud", "Hinjewadi"],
                "Total Accounts": [12000, 8500, 4500, 3000],
                "Active %": [92, 85, 95, 80],
                "Coverage Lead": ["FI Cell", "BC Supervisor", "Branch Ops", "District Co-ord"],
            }
        ),
        "note_templates": ["Low BC Utilisation Note", "PMJDY Campaign Circular", "FI Review Note"],
        "focus_items": [
            "Two BC locations remain below transaction activity threshold for the month.",
            "Hinjewadi branch needs a catch-up drive to improve account activation.",
            "Aadhaar seeding exceptions are concentrated in three rural service points.",
        ],
        "circulars": [
            ("RBI Master Circular on Financial Inclusion", "Aligned"),
            ("PMJDY outreach review agenda", "For next weekly meeting"),
        ],
        "drafts": ["FI monthly review note - April", "BC utilization escalation memo"],
        "analytics_y": "Total Accounts",
    },
}


def notice_board() -> list[tuple[str, str]]:
    return [
        ("Urgent", "Q4 compliance deadline has been extended by two working days."),
        ("Announcement", "Top performing branches for Q3 have been shortlisted for recognition."),
        ("System", "CBS maintenance is scheduled for Sunday 02:00 to 04:30."),
    ]


def complaints_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ID": ["C-100", "C-101", "C-102"],
            "Source": ["Branch Walk-in", "RBI IOS", "Email"],
            "TAT Days": [5, 28, 12],
            "Status": ["In Progress", "Critical", "Assigned"],
            "Owner": ["Customer Service", "RM Office", "CRMD Desk"],
        }
    )


def scorecard_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Branch": ["Pune Main", "Andheri", "Thane", "Kothrud"],
            "Business Growth": [12, 15, 8, 10],
            "PSL Achievement": [42, 38, 40, 45],
            "NPA Ratio": [2.1, 5.5, 3.2, 1.8],
            "Score": [85, 62, 74, 91],
        }
    )


def vault_docs() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Doc ID": ["DOC-892", "DOC-891", "DOC-870"],
            "Title": [
                "Monthly PMJDY Return (March 2026)",
                "OTS Proposal - XYZ Corp",
                "Branch Visit Review - Thane",
            ],
            "Department": ["FI", "CRMD", "ALL"],
            "Type": ["Returns", "Office Notes", "Letters"],
            "Date Submitted": ["2026-04-07", "2026-04-12", "2026-04-16"],
            "Author": ["fi_head", "crmd_head", "rm"],
        }
    )


def vendors_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Name": ["Adv. Sharma", "Desai & Co.", "TechSolutions Ltd", "Axis Security Services"],
            "Category": ["Panel Advocates", "Chartered Accountants", "IT Vendors", "Security Agencies"],
            "District": ["Pune", "Mumbai", "All", "Nashik"],
            "Empanelled Until": ["2027-01-15", "2026-11-20", "2028-05-01", "2026-08-30"],
            "Rating": [4, 3, 5, 4],
        }
    )


def visits_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Branch": ["Pune Main", "Thane", "Andheri"],
            "Date": ["2026-03-10", "2026-04-05", "2026-04-18"],
            "Status": ["Report Approved", "Pending Sign-off", "Action points open"],
            "Officer": ["RM Office", "CRMD Desk", "FI Cell"],
        }
    )
