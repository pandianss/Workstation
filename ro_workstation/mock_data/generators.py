import pandas as pd
import numpy as np

BRANCHES = [
    "Dindigul Main", "Palani", "Oddanchatram", "Vedasandur", "Natham",
    "Nilakottai", "Batlagundu", "Kodaikanal", "Athoor", "Guziliamparai",
    "Vadamadurai", "Reddiarchatram", "Thoppampatti", "Kosavapatti", "Ayakudi"
]

def _generate_df(metrics: dict) -> pd.DataFrame:
    np.random.seed(42) # Keep it consistent across loads
    data = {"Branch": BRANCHES}
    for metric, (low, high, is_int) in metrics.items():
        if is_int:
            data[metric] = np.random.randint(low, high, len(BRANCHES))
        else:
            data[metric] = np.round(np.random.uniform(low, high, len(BRANCHES)), 2)
    return pd.DataFrame(data)

def get_fi_data():
    df = _generate_df({
        "PMJDY Accounts": (1000, 15000, True),
        "Active %": (60, 99, False),
        "BC Outlets": (1, 5, True),
        "Aadhaar Seeding %": (70, 99, False)
    })
    kpis = {
        "Total PMJDY": df["PMJDY Accounts"].sum(),
        "Avg Active %": round(df["Active %"].mean(), 2),
        "Total BCs": df["BC Outlets"].sum(),
        "Avg Aadhaar %": round(df["Aadhaar Seeding %"].mean(), 2)
    }
    return kpis, df

def get_plan_data():
    df = _generate_df({
        "Deposits (Cr)": (50, 500, False),
        "Advances (Cr)": (30, 400, False),
        "CASA %": (25, 60, False),
        "CD Ratio %": (40, 110, False)
    })
    kpis = {
        "Total Deposits (Cr)": round(df["Deposits (Cr)"].sum(), 2),
        "Total Advances (Cr)": round(df["Advances (Cr)"].sum(), 2),
        "Overall CASA %": round(df["CASA %"].mean(), 2),
        "Overall CD Ratio %": round((df["Advances (Cr)"].sum() / df["Deposits (Cr)"].sum()) * 100, 2)
    }
    return kpis, df

def get_arid_data():
    df = _generate_df({
        "Agri Credit (Cr)": (10, 150, False),
        "KCC Accounts": (500, 5000, True),
        "SHG Linked": (20, 200, True),
        "Agri NPA %": (1, 15, False)
    })
    kpis = {
        "Total Agri (Cr)": round(df["Agri Credit (Cr)"].sum(), 2),
        "Total KCC": df["KCC Accounts"].sum(),
        "Total SHG": df["SHG Linked"].sum(),
        "Avg Agri NPA %": round(df["Agri NPA %"].mean(), 2)
    }
    return kpis, df

def get_hrdd_data():
    df = _generate_df({
        "Officers": (3, 15, True),
        "Clerks": (2, 10, True),
        "Sub-staff": (1, 5, True),
        "Vacancies": (0, 3, True)
    })
    kpis = {
        "Total Officers": df["Officers"].sum(),
        "Total Clerks": df["Clerks"].sum(),
        "Total Sub-staff": df["Sub-staff"].sum(),
        "Total Vacancies": df["Vacancies"].sum()
    }
    return kpis, df

def get_gad_data():
    df = _generate_df({
        "Premises Area (sqft)": (1000, 5000, True),
        "Lease Expiry (Days)": (30, 1500, True),
        "Security Staff": (1, 3, True),
        "Monthly Rent (Rs)": (20000, 150000, True)
    })
    kpis = {
        "Total Area (sqft)": df["Premises Area (sqft)"].sum(),
        "Avg Rent (Rs)": round(df["Monthly Rent (Rs)"].mean(), 2),
        "Leases Expiring < 90 Days": len(df[df["Lease Expiry (Days)"] < 90]),
        "Total Security": df["Security Staff"].sum()
    }
    return kpis, df

def get_crmd_data():
    df = _generate_df({
        "Gross NPA (Cr)": (2, 30, False),
        "NPA %": (1.5, 12.0, False),
        "SMA-2 Accounts": (5, 50, True),
        "SARFAESI Pending": (1, 10, True)
    })
    kpis = {
        "Total Gross NPA (Cr)": round(df["Gross NPA (Cr)"].sum(), 2),
        "Avg NPA %": round(df["NPA %"].mean(), 2),
        "Total SMA-2": df["SMA-2 Accounts"].sum(),
        "SARFAESI Pending": df["SARFAESI Pending"].sum()
    }
    return kpis, df

def get_com_data():
    df = _generate_df({
        "Open Audit Obs.": (0, 20, True),
        "KYC Exceptions": (10, 500, True),
        "STR Submissions": (0, 5, True),
        "Circular Compliance %": (80, 100, False)
    })
    kpis = {
        "Total Open Obs.": df["Open Audit Obs."].sum(),
        "Total KYC Exceptions": df["KYC Exceptions"].sum(),
        "Total STRs": df["STR Submissions"].sum(),
        "Avg Compliance %": round(df["Circular Compliance %"].mean(), 2)
    }
    return kpis, df

def get_mkt_data():
    df = _generate_df({
        "New SA Accts (YTD)": (500, 5000, True),
        "Cross Sell (Mktg)": (50, 500, True),
        "Leads Generated": (100, 1000, True),
        "Lead Conv. %": (10, 50, False)
    })
    kpis = {
        "Total New SA": df["New SA Accts (YTD)"].sum(),
        "Total Cross Sell": df["Cross Sell (Mktg)"].sum(),
        "Total Leads": df["Leads Generated"].sum(),
        "Avg Conv. %": round(df["Lead Conv. %"].mean(), 2)
    }
    return kpis, df

def get_law_data():
    df = _generate_df({
        "Suit Filed Cases": (5, 50, True),
        "Amount Involved (Cr)": (1, 20, False),
        "DRT Cases": (1, 15, True),
        "Lok Adalat Settled": (0, 10, True)
    })
    kpis = {
        "Total Suit Cases": df["Suit Filed Cases"].sum(),
        "Total Amt (Cr)": round(df["Amount Involved (Cr)"].sum(), 2),
        "Total DRT": df["DRT Cases"].sum(),
        "Lok Adalat Settled": df["Lok Adalat Settled"].sum()
    }
    return kpis, df

def get_ins_data():
    df = _generate_df({
        "Audit Rating": (1, 4, True), # 1=A, 2=B, 3=C, 4=D
        "Critical Obs.": (0, 5, True),
        "Major Obs.": (2, 15, True),
        "Irregularities": (0, 3, True)
    })
    kpis = {
        "Avg Rating": round(df["Audit Rating"].mean(), 1),
        "Total Critical": df["Critical Obs."].sum(),
        "Total Major": df["Major Obs."].sum(),
        "Total Irregularities": df["Irregularities"].sum()
    }
    return kpis, df

def get_rsk_data():
    df = _generate_df({
        "Risk Score": (10, 100, True),
        "Fraud Cases": (0, 2, True),
        "Cyber Incidents": (0, 3, True),
        "Cash Shortages": (0, 5, True)
    })
    kpis = {
        "Avg Risk Score": round(df["Risk Score"].mean(), 2),
        "Total Frauds": df["Fraud Cases"].sum(),
        "Cyber Incidents": df["Cyber Incidents"].sum(),
        "Total Cash Short": df["Cash Shortages"].sum()
    }
    return kpis, df

def get_sme_data():
    df = _generate_df({
        "MSME Credit (Cr)": (20, 200, False),
        "MUDRA Disbursed (L)": (50, 500, False),
        "CGTMSE Covered (Cr)": (5, 50, False),
        "MSME NPA %": (2, 18, False)
    })
    kpis = {
        "Total MSME (Cr)": round(df["MSME Credit (Cr)"].sum(), 2),
        "Total MUDRA (L)": round(df["MUDRA Disbursed (L)"].sum(), 2),
        "Total CGTMSE (Cr)": round(df["CGTMSE Covered (Cr)"].sum(), 2),
        "Avg MSME NPA %": round(df["MSME NPA %"].mean(), 2)
    }
    return kpis, df

def get_ret_data():
    df = _generate_df({
        "Home Loans (Cr)": (10, 150, False),
        "Auto Loans (Cr)": (5, 50, False),
        "Personal Loans (Cr)": (2, 20, False),
        "Retail NPA %": (0.5, 5.0, False)
    })
    kpis = {
        "Total HL (Cr)": round(df["Home Loans (Cr)"].sum(), 2),
        "Total AL (Cr)": round(df["Auto Loans (Cr)"].sum(), 2),
        "Total PL (Cr)": round(df["Personal Loans (Cr)"].sum(), 2),
        "Avg Retail NPA %": round(df["Retail NPA %"].mean(), 2)
    }
    return kpis, df

def get_rcc_data():
    df = _generate_df({
        "CBS Uptime %": (95, 100, False),
        "ATM Uptime %": (80, 100, False),
        "Open IT Tickets": (0, 15, True),
        "Hardware Reqs": (0, 5, True)
    })
    kpis = {
        "Avg CBS Uptime %": round(df["CBS Uptime %"].mean(), 2),
        "Avg ATM Uptime %": round(df["ATM Uptime %"].mean(), 2),
        "Total Open Tickets": df["Open IT Tickets"].sum(),
        "Total HW Reqs": df["Hardware Reqs"].sum()
    }
    return kpis, df
