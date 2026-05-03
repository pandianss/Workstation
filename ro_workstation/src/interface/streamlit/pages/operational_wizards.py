from __future__ import annotations
import datetime
import json
import pandas as pd
import streamlit as st
from src.application.services.wizard_service import WizardService
from src.interface.streamlit.state.services import (
    get_doc_service, get_circular_service, get_master_service
)
from src.infrastructure.persistence.database import get_db_session
from src.interface.streamlit.components.primitives import render_action_bar

def render() -> None:
    render_action_bar("Operations & Returns", ["Gallery", "Archive", "Requests"])

    tabs = st.tabs(["🏗️ Active Wizards", "🗄️ Document Archive"])
    
    with tabs[0]:
        if "wizard_selection" not in st.session_state:
            st.session_state["wizard_selection"] = None

        if st.session_state["wizard_selection"] is None:
            render_wizard_gallery()
        else:
            if st.button("⬅️ Back to Gallery", key="back_to_gallery"):
                st.session_state["wizard_selection"] = None
                # Clear all wizard data keys
                for key in list(st.session_state.keys()):
                    if any(x in key for x in ["data", "step", "last_pdf"]):
                        del st.session_state[key]
                st.rerun()
            render_selected_wizard()
            
    with tabs[1]:
        render_document_archive()

def render_wizard_gallery() -> None:
    st.markdown("### 🛠️ Operations & Returns Command Center")
    st.caption("Consolidated workspace for all regional documents, statutory returns, and operational tools.")

    categories = {
        "Returns & Compliance": [
            {"id": "dicgc", "title": "DICGC Half-Yearly Return", "desc": "Standard Form DI-01 reporting and premium assessment.", "icon": "📊"},
            {"id": "statutory_returns", "title": "Statutory Compliance", "desc": "Track and monitor periodic return submissions.", "icon": "🛡️"},
            {"id": "branch_visits", "title": "Executive Branch Visits", "desc": "Record and report Region Head branch visit observations.", "icon": "🚗"},
        ],
        "Document Generators": [
            {"id": "office_note", "title": "Office Note Generator", "desc": "Create trilingual office notes for approvals.", "icon": "📝"},
            {"id": "circular_drafter", "title": "Circular Drafter", "desc": "Draft and issue official regional circulars.", "icon": "📜"},
            {"id": "anniversary_note", "title": "Anniversary Note", "desc": "Generate branch anniversary congratulatory notes.", "icon": "🎉"},
            {"id": "survey_viability", "title": "Survey & Viability", "desc": "Market research and new unit viability studies.", "icon": "📋"},
        ],
        "Operational Tools": [
            {"id": "broken_interest", "title": "Broken Period Interest", "desc": "Calculate & justify interest for non-standard periods.", "icon": "📈"},
            {"id": "rbi_proforma", "title": "RBI Proforma Reporting", "desc": "Report branch openings/updates to RBI.", "icon": "🏦"},
            {"id": "expense_approval", "title": "Expense Approval", "desc": "Request approval for administrative expenses.", "icon": "💸"},
            {"id": "gl_activation", "title": "GL Head Activation", "desc": "Activate or modify General Ledger heads.", "icon": "📒"},
        ],
        "Specialized Requests": [
            {"id": "high_value_dd", "title": "High Value DD", "desc": "Report high-value Demand Drafts issued.", "icon": "✉️"},
            {"id": "micr_request", "title": "MICR/Cheque Request", "desc": "Request MICR codes or new cheque series.", "icon": "🎫"},
            {"id": "proforma_branch", "title": "Proforma Branch Code", "desc": "Core banking setup data for branches.", "icon": "🏢"},
            {"id": "reversal_charges", "title": "Reversal of Charges", "desc": "Request waiver or reversal of bank charges.", "icon": "🔄"},
        ],
        "Automation": [
            {"id": "mail_merge", "title": "Bulk Mail Merge", "desc": "Generate personalized documents from Excel data.", "icon": "📬"},
        ]
    }

    for cat_name, wizard_list in categories.items():
        with st.expander(f"{cat_name}", expanded=(cat_name == "Operational Tools")):
            cols = st.columns(2)
            for i, wizard in enumerate(wizard_list):
                with cols[i % 2]:
                    st.markdown(
                        f"""
                        <div class="glass-panel" style="margin-bottom: 15px; border-left: 4px solid #3b82f6;">
                            <div style="font-size: 1.5rem; margin-bottom: 8px;">{wizard['icon']}</div>
                            <div style="font-weight: 700; font-size: 1.1rem;">{wizard['title']}</div>
                            <div style="font-size: 0.85rem; opacity: 0.8; margin-bottom: 12px;">{wizard['desc']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Launch {wizard['title']}", key=f"btn_{wizard['id']}", use_container_width=True):
                        st.session_state["wizard_selection"] = wizard['id']
                        st.rerun()

def render_selected_wizard() -> None:
    wid = st.session_state["wizard_selection"]
    
    st.divider()

    if wid == "broken_interest":
        render_broken_interest_wizard()
    elif wid == "dicgc":
        from src.interface.streamlit.pages import dicgc
        dicgc.render()
    elif wid == "statutory_returns":
        from src.interface.streamlit.pages import returns
        returns.render()
    elif wid == "branch_visits":
        from src.interface.streamlit.pages import visits
        visits.render()
    elif wid == "office_note":
        render_office_note_wizard()
    elif wid == "circular_drafter":
        render_circular_drafter_wizard()
    elif wid == "anniversary_note":
        render_anniversary_note_wizard()
    elif wid == "mail_merge":
        render_mail_merge_wizard()
    elif wid == "survey_viability":
        from src.interface.streamlit.pages import surveys
        surveys.render()
    elif wid == "high_value_dd":
        render_high_value_dd_wizard()
    elif wid == "micr_request":
        render_micr_request_wizard()
    elif wid == "proforma_branch":
        render_proforma_branch_wizard()
    elif wid == "reversal_charges":
        render_reversal_charges_wizard()
    elif wid == "rbi_proforma":
        render_rbi_proforma_wizard()
    else:
        st.info(f"Wizard '{wid}' is coming soon.")

def render_expense_approval_wizard() -> None:
    st.markdown("### 💸 Expense Approval Wizard")
    if "exp_step" not in st.session_state: st.session_state["exp_step"] = 1
    if "exp_data" not in st.session_state:
        st.session_state["exp_data"] = {
            "category": "REVENUE", "budget_head": "", "custom_head": "",
            "allocated": 0.0, "utilized": 0.0, "purpose": "",
            "amount": 0.0, "quotation_basis": "L1", "quotation_details": "",
            "vendor_name": "", "vendor_pan": "", "vendor_gst": "",
            "tds": "Yes", "gst": "Yes", "recommendation": ""
        }
    
    exp = st.session_state["exp_data"]
    
    if st.session_state["exp_step"] == 1:
        st.markdown("#### Step 1: Categorization & Budget")
        col1, col2 = st.columns(2)
        exp["category"] = col1.selectbox("Expense Category", ["REVENUE", "CAPITAL"])
        heads = ["Repairs and Maintenance", "Printing and Stationery", "Advertisement and Publicity", "Travelling Expenses", "Legal Charges", "Other Expenditure (Sundries)", "Custom"]
        exp["budget_head"] = col2.selectbox("Budget Head", heads)
        if exp["budget_head"] == "Custom":
            exp["custom_head"] = st.text_input("Specify Budget Head", value=exp["custom_head"])
        
        if exp["budget_head"] == "Other Expenditure (Sundries)":
            c1, c2 = st.columns(2)
            exp["allocated"] = c1.number_input("Allocated Budget (₹)", value=exp["allocated"])
            exp["utilized"] = c2.number_input("Utilized till Date (₹)", value=exp["utilized"])

    elif st.session_state["exp_step"] == 2:
        st.markdown("#### Step 2: Proposal & Vendor")
        exp["purpose"] = st.text_area("Purpose & Details", value=exp["purpose"])
        col1, col2 = st.columns(2)
        exp["amount"] = col1.number_input("Proposed Amount (₹)", value=exp["amount"])
        exp["quotation_basis"] = col2.selectbox("Quotation Basis", ["L1", "SINGLE", "EMPANELED", "NA"])
        
        if exp["quotation_basis"] == "L1":
            exp["quotation_details"] = st.text_area("Quotation Details", value=exp["quotation_details"])
            
        st.divider()
        st.caption("Vendor Information")
        exp["vendor_name"] = st.text_input("Vendor Name", value=exp["vendor_name"])
        c1, c2 = st.columns(2)
        exp["vendor_pan"] = c1.text_input("Vendor PAN", value=exp["vendor_pan"])
        exp["vendor_gst"] = c2.text_input("Vendor GSTIN", value=exp["vendor_gst"])

    elif st.session_state["exp_step"] == 3:
        st.markdown("#### Step 3: Statutory & Final")
        col1, col2 = st.columns(2)
        exp["tds"] = col1.selectbox("TDS Applicable?", ["Yes", "No"])
        exp["gst"] = col2.selectbox("GST Applicable?", ["Yes", "No"])
        exp["recommendation"] = st.text_area("Final Recommendation", value=exp["recommendation"])
        
        if st.button("💾 Save Expense Proposal", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("expense_approval", st.session_state.get("username", "USER"), exp, subject=f"Expense: {exp['budget_head']} - ₹{exp['amount']}")
                st.success("Expense proposal saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["exp_step"] > 1:
        if c1.button("⬅️ Previous", key="exp_prev"):
            st.session_state["exp_step"] -= 1
            st.rerun()
    if st.session_state["exp_step"] < 3:
        if c2.button("Next ➡️", key="exp_next"):
            st.session_state["exp_step"] += 1
            st.rerun()

def render_gl_activation_wizard() -> None:
    st.markdown("### 📒 GL Head Activation Wizard")
    if "gl_step" not in st.session_state: st.session_state["gl_step"] = 1
    if "gl_data" not in st.session_state:
        st.session_state["gl_data"] = {
            "account_no": "", "desc": "", "dept": "", "user": "",
            "purpose": "", "op_type": "System", "dr_cr": "Both", "class": "Liability",
            "activity": "Generic", "limits": "No", "monitoring": "",
            "op_by": "Branch only", "cash_op": "No", "recon": "Reconciliation to zero by same day"
        }
    
    gl = st.session_state["gl_data"]
    
    if st.session_state["gl_step"] == 1:
        st.markdown("#### Step 1: Identifiers")
        col1, col2 = st.columns(2)
        gl["account_no"] = col1.text_input("Proposed GL Account No", value=gl["account_no"])
        gl["desc"] = col2.text_input("GL Head Name", value=gl["desc"])
        gl["dept"] = col1.text_input("Ownership Department", value=gl["dept"])
        gl["user"] = col2.text_input("Operation End User", value=gl["user"])

    elif st.session_state["gl_step"] == 2:
        st.markdown("#### Step 2: Technical Details")
        gl["purpose"] = st.text_area("Detailed Purpose", value=gl["purpose"])
        c1, c2 = st.columns(2)
        gl["op_type"] = c1.selectbox("Operation Type", ["System", "Manual", "Both"])
        gl["dr_cr"] = c2.selectbox("Debit / Credit / Both", ["Debit", "Credit", "Both"])
        gl["class"] = c1.selectbox("Asset / Liability Class", ["Liability", "Asset", "Income", "Expense"])
        gl["activity"] = c2.text_input("Activity Type", value=gl["activity"])

    elif st.session_state["gl_step"] == 3:
        st.markdown("#### Step 3: Controls")
        c1, c2 = st.columns(2)
        gl["limits"] = c1.selectbox("Limits Applicable?", ["Yes", "No"])
        gl["monitoring"] = c2.text_input("Monitoring Department", value=gl["monitoring"])
        gl["op_by"] = c1.selectbox("Operation By", ["Branch only", "RO only", "Both"])
        gl["cash_op"] = c2.selectbox("Cash Operation Allowed?", ["Yes", "No"])
        gl["recon"] = st.text_area("Reconciliation Mandate", value=gl["recon"])
        
        if st.button("💾 Submit GL Activation", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("gl_activation", st.session_state.get("username", "USER"), gl, subject=f"GL Activation: {gl['desc']}")
                st.success("GL Activation request saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["gl_step"] > 1:
        if c1.button("⬅️ Previous", key="gl_prev"):
            st.session_state["gl_step"] -= 1
            st.rerun()
    if st.session_state["gl_step"] < 3:
        if c2.button("Next ➡️", key="gl_next"):
            st.session_state["gl_step"] += 1
            st.rerun()

def render_broken_interest_wizard() -> None:
    st.markdown("### 📈 Broken Period Interest Calculator")
    
    if "wiz_step" not in st.session_state: st.session_state["wiz_step"] = 1
    if "wiz_data" not in st.session_state:
        st.session_state["wiz_data"] = {
            "depositor_type": "Individual",
            "category": "General",
            "cif_id": "",
            "account_no": "",
            "open_date": datetime.date.today(),
            "dob": datetime.date(1980, 1, 1),
            "age": 0,
            "principal": 100000.0,
            "base_rate": 6.50,
            "spread": 0.0,
            "effective_rate": 6.50,
            "start_date": datetime.date.today() - datetime.timedelta(days=30),
            "end_date": datetime.date.today(),
            "days": 30,
            "frequency": "SIMPLE",
            "interest_amount": 0.0,
            "justification": ""
        }
    
    data = st.session_state["wiz_data"]
    
    # Step 1: Depositor Details
    if st.session_state["wiz_step"] == 1:
        st.markdown("#### Step 1: Depositor & Account Details")
        col1, col2 = st.columns(2)
        with col1:
            data["depositor_type"] = st.selectbox("Depositor Type", ["Individual", "Organization"], index=0 if data["depositor_type"] == "Individual" else 1)
            data["category"] = st.selectbox("Customer Category", ["General", "Senior Citizen", "Super Senior Citizen"], index=["General", "Senior Citizen", "Super Senior Citizen"].index(data["category"]))
            data["cif_id"] = st.text_input("CIF ID / Customer ID", value=data["cif_id"])
        with col2:
            data["account_no"] = st.text_input("TD / FD Account Number", value=data["account_no"])
            data["open_date"] = st.date_input("Deposit Open Date", value=data["open_date"])
            if data["depositor_type"] == "Individual":
                data["dob"] = st.date_input("Date of Birth", value=data["dob"])
                # Auto-calc age
                today = datetime.date.today()
                data["age"] = today.year - data["dob"].year - ((today.month, today.day) < (data["dob"].month, data["dob"].day))
                st.info(f"Calculated Age: {data['age']} years")
                
                # Auto-set spread based on age/category
                if data["category"] == "Senior Citizen": data["spread"] = 0.50
                elif data["category"] == "Super Senior Citizen": data["spread"] = 0.75
                else: data["spread"] = 0.0
            else:
                data["spread"] = 0.0
                st.caption("Age and Senior Citizen spread not applicable for Organizations.")

    # Step 2: Rate & Period
    elif st.session_state["wiz_step"] == 2:
        st.markdown("#### Step 2: Interest Criteria & Period")
        col1, col2 = st.columns(2)
        with col1:
            data["principal"] = st.number_input("Principal / Deposit Amount (₹)", value=data["principal"], step=1000.0)
            data["base_rate"] = st.number_input("Base Interest Rate (%)", value=data["base_rate"], step=0.05)
            data["spread"] = st.number_input("Additional Spread (%)", value=data["spread"], step=0.05)
            data["effective_rate"] = data["base_rate"] + data["spread"]
            st.metric("Effective Interest Rate", f"{data['effective_rate']}%")
        with col2:
            data["start_date"] = st.date_input("Period Start Date", value=data["start_date"])
            data["end_date"] = st.date_input("Period End Date", value=data["end_date"])
            data["days"] = (data["end_date"] - data["start_date"]).days
            st.metric("Broken Period Days", f"{data['days']} days")
            
            data["frequency"] = st.selectbox("Compounding Frequency", ["SIMPLE", "QUARTERLY", "MONTHLY", "HALFYEARLY", "ANNUALLY"])
            
        # Calculation
        with get_db_session() as session:
            svc = WizardService(session)
            data["interest_amount"] = svc.calculate_broken_period_interest(data["principal"], data["effective_rate"], data["days"], data["frequency"])
            
        st.success(f"Calculated Interest Amount: **₹ {data['interest_amount']:,.2f}**")

    # Step 3: Justification & Save
    elif st.session_state["wiz_step"] == 3:
        st.markdown("#### Step 3: Justification & Finalization")
        data["justification"] = st.text_area("Justification for Broken Period Interest", value=data["justification"], help="Provide technical or business justification for this payout.")
        
        if st.button("💾 Save Submission", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("broken_interest", st.session_state.get("username", "USER"), data, subject=f"Interest: {data['account_no']}")
                st.success("Submission saved to archive! You can download the PDF from the 'Document Archive' tab.")
                st.session_state["last_sub_id"] = sub.id

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["wiz_step"] > 1:
        if c1.button("⬅️ Previous"):
            st.session_state["wiz_step"] -= 1
            st.rerun()
    if st.session_state["wiz_step"] < 3:
        if c2.button("Next ➡️"):
            st.session_state["wiz_step"] += 1
            st.rerun()

def render_rbi_proforma_wizard() -> None:
    st.markdown("### 🏦 RBI Proforma Reporting Wizard")
    
    if "rbi_step" not in st.session_state: st.session_state["rbi_step"] = 1
    if "rbi_data" not in st.session_state:
        st.session_state["rbi_data"] = {
            "action": "ADDITION", "outlet_class": "BM_BRANCH",
            "update_part_i": "", "update_eff_date": datetime.date.today(),
            "conv_from": "", "conv_to": "", "conv_part_i": "", "conv_date": datetime.date.today(),
            "bm_domestic": "DOMESTIC",
            "bc_type": "CORPORATE", "bc_base_part_i": "", "bc_iba_reg": "",
            "office_domestic": "DOMESTIC", "office_type": "", "office_type_other": "", "office_base_part_i": "",
            "naio_type": "", "naio_type_other": "", "naio_base_part_i": "",
            "csp_mode": "", "csp_mode_other": "", "csp_onsite": "ONSITE", "csp_manned": "MANNED", "csp_base_part_i": "",
            "outlet_name": "", "app_category": "GENERAL_PERMISSION", "opening_date": datetime.date.today(),
            "licence_no": "", "licence_date": datetime.date.today(), "reval_ref": "", "reval_date": datetime.date.today(),
            "currency_chest_part_i": "",
            "micr": "", "ifsc": "", "cbs_code": "",
            "country": "INDIA", "state": "TAMIL NADU", "district": "DINDIGUL", "sub_district": "", "revenue_centre": "",
            "addr1": "", "addr2": "", "post_office": "", "pin": "",
            "long": "", "lat": "",
            "contact_name": "", "tel": "", "mobile": "", "fax": "", "email": "",
            "working_type": "FULL_TIME", "full_time_hours": "10:00 - 16:00, Mon-Sat",
            "schedule": {}, # For part-time
            "additional_centres": "",
            "services": {}, # Checkboxes
            "forex_ad_cat": "", "forex_auth_date": datetime.date.today(), "forex_settling_part_i": "",
            "remarks": ""
        }
    
    rbi = st.session_state["rbi_data"]
    
    # Step 1: Action & Class
    if st.session_state["rbi_step"] == 1:
        st.markdown("#### Step 1: Action & Outlet Class")
        col1, col2 = st.columns(2)
        with col1:
            rbi["action"] = st.selectbox("Action for Reporting", ["ADDITION", "UPDATION", "CLOSURE", "MERGED", "CONVERSION"], index=["ADDITION", "UPDATION", "CLOSURE", "MERGED", "CONVERSION"].index(rbi["action"]))
        with col2:
            rbi["outlet_class"] = st.selectbox("Outlet / Unit Class", ["BM_BRANCH", "FIXED_BC", "OFFICE", "NAIO", "OTHER_CSP"], index=["BM_BRANCH", "FIXED_BC", "OFFICE", "NAIO", "OTHER_CSP"].index(rbi["outlet_class"]))
            
        if rbi["action"] == "UPDATION":
            st.divider()
            c1, c2 = st.columns(2)
            rbi["update_part_i"] = c1.text_input("Part-I Code (being updated)", value=rbi["update_part_i"])
            rbi["update_eff_date"] = c2.date_input("Effective Date of Change", value=rbi["update_eff_date"])
        elif rbi["action"] == "CONVERSION":
            st.divider()
            c1, c2 = st.columns(2)
            rbi["conv_from"] = c1.text_input("Conversion From", value=rbi["conv_from"])
            rbi["conv_to"] = c2.text_input("Conversion To", value=rbi["conv_to"])
            rbi["conv_part_i"] = c1.text_input("Part-I Code", value=rbi["conv_part_i"])
            rbi["conv_date"] = c2.date_input("Conversion Date", value=rbi["conv_date"])

    # Step 2: Class Specific Details
    elif st.session_state["rbi_step"] == 2:
        st.markdown(f"#### Step 2: {rbi['outlet_class'].replace('_', ' ')} Details")
        if rbi["outlet_class"] == "BM_BRANCH":
            rbi["bm_domestic"] = st.selectbox("Domestic / Overseas Banking Unit", ["DOMESTIC", "OVERSEAS"], index=0 if rbi["bm_domestic"] == "DOMESTIC" else 1)
        elif rbi["outlet_class"] == "FIXED_BC":
            c1, c2 = st.columns(2)
            rbi["bc_type"] = c1.selectbox("BC Type", ["CORPORATE", "INDIVIDUAL"], index=0 if rbi["bc_type"] == "CORPORATE" else 1)
            rbi["bc_base_part_i"] = c2.text_input("Base/Controlling Branch Part-I Code", value=rbi["bc_base_part_i"])
            rbi["bc_iba_reg"] = st.text_input("IBA Registration Number", value=rbi["bc_iba_reg"])
        elif rbi["outlet_class"] == "OFFICE":
            c1, c2 = st.columns(2)
            rbi["office_domestic"] = c1.selectbox("Domestic / Overseas", ["DOMESTIC", "OVERSEAS"])
            rbi["office_type"] = c2.selectbox("Office Type", ["ADMIN", "TRAINING_CENTRE", "CPC", "SERVICE_BRANCH", "ASSET_RECOVERY", "TREASURY", "FOREX", "OTHER"])
            if rbi["office_type"] == "OTHER":
                rbi["office_type_other"] = st.text_input("Specify Office Type", value=rbi["office_type_other"])
            rbi["office_base_part_i"] = st.text_input("Part-I Code of Base Branch/Office", value=rbi["office_base_part_i"])
        elif rbi["outlet_class"] == "NAIO":
            c1, c2 = st.columns(2)
            rbi["naio_type"] = c1.selectbox("NAIO Type", ["EXTENSION_COUNTER", "SATELLITE_OFFICE", "EXCHANGE_BUREAU", "REP_OFFICE", "CALL_CENTRE", "OTHER"])
            if rbi["naio_type"] == "OTHER":
                rbi["naio_type_other"] = c2.text_input("Specify NAIO Type", value=rbi["naio_type_other"])
            rbi["naio_base_part_i"] = st.text_input("Part-I Code of Base BO/Office", value=rbi["naio_base_part_i"])
        elif rbi["outlet_class"] == "OTHER_CSP":
            c1, c2 = st.columns(2)
            rbi["csp_mode"] = c1.selectbox("Mode of Service", ["ATM", "CRM", "BNAM_CDM", "EKIOSK", "ELOBBY", "ELECTRONIC_OTHER", "MANUAL_OTHER"])
            if rbi["csp_mode"] in ["ELECTRONIC_OTHER", "MANUAL_OTHER"]:
                rbi["csp_mode_other"] = c2.text_input("Specify Service Mode", value=rbi["csp_mode_other"])
            rbi["csp_onsite"] = c1.selectbox("Onsite / Off-site", ["ONSITE", "OFFSITE"])
            rbi["csp_manned"] = c2.selectbox("Manned / Unmanned", ["MANNED", "UNMANNED"])
            rbi["csp_base_part_i"] = st.text_input("Part-I Code of Base BO/Office", value=rbi["csp_base_part_i"])

    # Step 3: Identity & License
    elif st.session_state["rbi_step"] == 3:
        st.markdown("#### Step 3: Identity & License Information")
        rbi["outlet_name"] = st.text_input("Name of Banking Outlet / Office / CSP *", value=rbi["outlet_name"])
        col1, col2 = st.columns(2)
        rbi["app_category"] = col1.selectbox("Applicable Category", ["GENERAL_PERMISSION", "WITH_AUTHORISATION"])
        rbi["opening_date"] = col2.date_input("Date of Opening (Actual / Planned) *", value=rbi["opening_date"])
        
        if rbi["app_category"] == "WITH_AUTHORISATION":
            st.divider()
            c1, c2 = st.columns(2)
            rbi["licence_no"] = c1.text_input("Licence / Authorisation Letter No.", value=rbi["licence_no"])
            rbi["licence_date"] = c2.date_input("Date of Licence Letter", value=rbi["licence_date"])
            rbi["reval_ref"] = c1.text_input("Re-validation Reference No.", value=rbi["reval_ref"])
            rbi["reval_date"] = c2.date_input("Date of Re-validation", value=rbi["reval_date"])
            
        st.divider()
        st.caption("Banking Codes")
        c1, c2, c3 = st.columns(3)
        rbi["micr"] = c1.text_input("MICR Code", value=rbi["micr"], max_chars=9)
        rbi["ifsc"] = c2.text_input("IFSC Code", value=rbi["ifsc"], max_chars=11)
        rbi["cbs_code"] = c3.text_input("CBS (Internal) Code", value=rbi["cbs_code"])

    # Step 4: Location & Contact
    elif st.session_state["rbi_step"] == 4:
        st.markdown("#### Step 4: Location & Communication")
        c1, c2, c3 = st.columns(3)
        rbi["country"] = c1.text_input("Country", value=rbi["country"])
        rbi["state"] = c2.text_input("State", value=rbi["state"])
        rbi["district"] = c3.text_input("District", value=rbi["district"])
        rbi["sub_district"] = c1.text_input("Sub-District", value=rbi["sub_district"])
        rbi["revenue_centre"] = c2.text_input("Revenue Centre", value=rbi["revenue_centre"])
        rbi["pin"] = c3.text_input("Pin Code", value=rbi["pin"], max_chars=6)
        
        st.divider()
        rbi["addr1"] = st.text_input("Address Line 1", value=rbi["addr1"])
        rbi["addr2"] = st.text_input("Address Line 2", value=rbi["addr2"])
        rbi["post_office"] = st.text_input("Name of Post Office", value=rbi["post_office"])
        
        st.divider()
        st.caption("Geo-coordinates & Contact")
        c1, c2 = st.columns(2)
        rbi["long"] = c1.text_input("Longitude", value=rbi["long"])
        rbi["lat"] = c2.text_input("Latitude", value=rbi["lat"])
        rbi["mobile"] = c1.text_input("Mobile No.", value=rbi["mobile"])
        rbi["email"] = c2.text_input("Email Address", value=rbi["email"])

    # Step 5: Operations & Services
    elif st.session_state["rbi_step"] == 5:
        st.markdown("#### Step 5: Operations & Services")
        rbi["working_type"] = st.radio("Working Days / Hours", ["FULL_TIME", "PART_TIME"], horizontal=True)
        if rbi["working_type"] == "FULL_TIME":
            rbi["full_time_hours"] = st.text_input("Working Hours (e.g. 10:00–16:00, Mon–Sat)", value=rbi["full_time_hours"])
        else:
            st.info("Part-time schedule data entry enabled. Using default banking hours for Spoke locations.")
            
        st.divider()
        st.caption("Services Offered (Check all that apply)")
        svcs = rbi.get("services", {})
        col1, col2, col3 = st.columns(3)
        svcs["general"] = col1.checkbox("General Banking", value=svcs.get("general", False))
        svcs["personal"] = col2.checkbox("Personal Banking", value=svcs.get("personal", False))
        svcs["locker"] = col3.checkbox("Locker Facility", value=svcs.get("locker", False))
        svcs["agri"] = col1.checkbox("Agri Finance", value=svcs.get("agri", False))
        svcs["msme"] = col2.checkbox("MSME Finance", value=svcs.get("msme", False))
        svcs["forex"] = col3.checkbox("Forex Business", value=svcs.get("forex", False))
        rbi["services"] = svcs
        
        st.divider()
        rbi["forex_ad_cat"] = st.selectbox("Forex AD Category", ["", "A", "B", "C"], index=["", "A", "B", "C"].index(rbi["forex_ad_cat"]))
        if rbi["forex_ad_cat"]:
            rbi["forex_auth_date"] = st.date_input("Date of Authorisation", value=rbi["forex_auth_date"])

    # Step 6: Review & Finalize
    elif st.session_state["rbi_step"] == 6:
        st.markdown("#### Step 6: Review & Finalize")
        rbi["remarks"] = st.text_area("Remarks / Additional Notes", value=rbi["remarks"])
        
        st.json(rbi)
        
        if st.button("🚀 Submit RBI Proforma", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("rbi_proforma", st.session_state.get("username", "USER"), rbi, subject=f"RBI: {rbi['outlet_name']}")
                st.success("RBI Proforma saved to archive! You can download the PDF from the 'Document Archive' tab.")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["rbi_step"] > 1:
        if c1.button("⬅️ Previous", key="rbi_prev"):
            st.session_state["rbi_step"] -= 1
            st.rerun()
    if st.session_state["rbi_step"] < 6:
        if c2.button("Next ➡️", key="rbi_next"):
            st.session_state["rbi_step"] += 1
            st.rerun()

def render_high_value_dd_wizard() -> None:
    st.markdown("### ✉️ High Value DD Reporting Wizard")
    if "dd_step" not in st.session_state: st.session_state["dd_step"] = 1
    if "dd_data" not in st.session_state:
        st.session_state["dd_data"] = {
            "sol_id": "", "grade": "", "applicant_name": "", "account_no": "",
            "kyc": "Yes", "issue_date": datetime.date.today(), "beneficiary": "",
            "drawn_on": "", "amount": 0.0, "trans_id": "", "purpose": ""
        }
    
    dd = st.session_state["dd_data"]
    
    if st.session_state["dd_step"] == 1:
        st.markdown("#### Step 1: Branch & Applicant")
        col1, col2 = st.columns(2)
        dd["sol_id"] = col1.text_input("Branch SOL ID", value=dd["sol_id"], max_chars=4)
        dd["applicant_name"] = col2.text_input("Applicant Name", value=dd["applicant_name"])
        dd["account_no"] = col1.text_input("Account Number", value=dd["account_no"])
        dd["kyc"] = col2.selectbox("KYC Compliance", ["Yes", "No"])

    elif st.session_state["dd_step"] == 2:
        st.markdown("#### Step 2: DD Details")
        col1, col2 = st.columns(2)
        dd["issue_date"] = col1.date_input("Date of Issue", value=dd["issue_date"])
        dd["beneficiary"] = col2.text_input("Beneficiary Name", value=dd["beneficiary"])
        dd["drawn_on"] = col1.text_input("DD Drawn on (Payable Branch)", value=dd["drawn_on"])
        dd["amount"] = col2.number_input("Amount of DD (₹)", value=dd["amount"])
        dd["trans_id"] = st.text_input("Transaction ID", value=dd["trans_id"])

    elif st.session_state["dd_step"] == 3:
        st.markdown("#### Step 3: Purpose & Finalize")
        dd["purpose"] = st.text_area("Purpose of Transaction", value=dd["purpose"])
        
        if st.button("🚀 Submit High Value DD Report", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("high_value_dd", st.session_state.get("username", "USER"), dd, subject=f"DD: {dd['beneficiary']} - ₹{dd['amount']}")
                st.success("High Value DD report saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["dd_step"] > 1:
        if c1.button("⬅️ Previous", key="dd_prev"):
            st.session_state["dd_step"] -= 1
            st.rerun()
    if st.session_state["dd_step"] < 3:
        if c2.button("Next ➡️", key="dd_next"):
            st.session_state["dd_step"] += 1
            st.rerun()

def render_micr_request_wizard() -> None:
    st.markdown("### 🎫 MICR/Cheque Request Wizard")
    if "micr_step" not in st.session_state: st.session_state["micr_step"] = 1
    if "micr_data" not in st.session_state:
        st.session_state["micr_data"] = {
            "opening_date": datetime.date.today(), "branch_name": "", "permission": "",
            "population": "RURAL", "taluk": "", "district": "", "cbs": "Yes",
            "address": "", "hours_week": "", "hours_sat": "", "hours_sun": "",
            "email": "", "tel": "", "purpose": "", "head_details": "", "ro_details": ""
        }
    
    micr = st.session_state["micr_data"]
    
    if st.session_state["micr_step"] == 1:
        st.markdown("#### Step 1: Branch Identity")
        col1, col2 = st.columns(2)
        micr["opening_date"] = col1.date_input("Date of Opening", value=micr["opening_date"])
        micr["branch_name"] = col2.text_input("Name of Branch/Office", value=micr["branch_name"])
        micr["permission"] = st.text_input("Permission Letter / License Details", value=micr["permission"])

    elif st.session_state["micr_step"] == 2:
        st.markdown("#### Step 2: Location & Operations")
        col1, col2 = st.columns(2)
        micr["population"] = col1.selectbox("Population Category", ["METRO", "URBAN", "SEMI-URBAN", "RURAL"])
        micr["taluk"] = col2.text_input("Taluk / Tehsil", value=micr["taluk"])
        micr["district"] = col1.text_input("District / State", value=micr["district"])
        micr["cbs"] = col2.selectbox("Under CBS?", ["Yes", "No"])
        micr["address"] = st.text_area("Postal Address", value=micr["address"])

    elif st.session_state["micr_step"] == 3:
        st.markdown("#### Step 3: Contact & Finalize")
        c1, c2, c3 = st.columns(3)
        micr["hours_week"] = c1.text_input("Weekdays", value=micr["hours_week"])
        micr["hours_sat"] = c2.text_input("Saturdays", value=micr["hours_sat"])
        micr["hours_sun"] = c3.text_input("Holiday", value=micr["hours_sun"])
        
        micr["email"] = st.text_input("Mail ID", value=micr["email"])
        micr["tel"] = st.text_input("Landline Number", value=micr["tel"])
        micr["purpose"] = st.text_area("Purpose of Request", value=micr["purpose"])
        
        if st.button("💾 Submit MICR Request", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("micr_request", st.session_state.get("username", "USER"), micr, subject=f"MICR: {micr['branch_name']}")
                st.success("MICR request saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["micr_step"] > 1:
        if c1.button("⬅️ Previous", key="micr_prev"):
            st.session_state["micr_step"] -= 1
            st.rerun()
    if st.session_state["micr_step"] < 3:
        if c2.button("Next ➡️", key="micr_next"):
            st.session_state["micr_step"] += 1
            st.rerun()

def render_proforma_branch_wizard() -> None:
    st.markdown("### 🏢 Proforma Branch Code Wizard")
    if "prof_step" not in st.session_state: st.session_state["prof_step"] = 1
    if "prof_data" not in st.session_state:
        st.session_state["prof_data"] = {
            "date_of_opening": datetime.date.today(), "branch_name": "", "permission_details": "",
            "population_category": "RURAL", "population_centre": "", "community_block": "",
            "taluk_tehsil": "", "district_state": "", "working_hours": "10:00 - 16:00",
            "postal_address": "", "currency_chest": "", "authorised_dealer": "",
            "under_cbs": "Yes", "micr_code": ""
        }
    
    prof = st.session_state["prof_data"]
    
    if st.session_state["prof_step"] == 1:
        st.markdown("#### Step 1: Identity & Location")
        col1, col2 = st.columns(2)
        prof["date_of_opening"] = col1.date_input("Date of Opening", value=prof["date_of_opening"])
        prof["branch_name"] = col2.text_input("Name of Branch / Office", value=prof["branch_name"])
        prof["permission_details"] = st.text_area("Permission Letter / License Details", value=prof["permission_details"])
        
    elif st.session_state["prof_step"] == 2:
        st.markdown("#### Step 2: Demographics")
        col1, col2 = st.columns(2)
        prof["population_category"] = col1.selectbox("Population Category", ["METRO", "URBAN", "SEMI-URBAN", "RURAL"])
        prof["population_centre"] = col2.text_input("Population Centre", value=prof["population_centre"])
        prof["community_block"] = col1.text_input("Community Development Block", value=prof["community_block"])
        prof["taluk_tehsil"] = col2.text_input("Taluk / Tehsil", value=prof["taluk_tehsil"])
        prof["district_state"] = st.text_input("District and State", value=prof["district_state"])
        
    elif st.session_state["prof_step"] == 3:
        st.markdown("#### Step 3: Logistics & CBS")
        prof["postal_address"] = st.text_area("Complete Postal Address with Pin Code", value=prof["postal_address"])
        prof["working_hours"] = st.text_input("Working Hours", value=prof["working_hours"])
        col1, col2 = st.columns(2)
        prof["currency_chest"] = col1.text_input("Nearest Currency Chest", value=prof["currency_chest"])
        prof["authorised_dealer"] = col2.text_input("Authorised Dealer (FX Routing)", value=prof["authorised_dealer"])
        prof["under_cbs"] = col1.selectbox("Under CBS?", ["Yes", "No"])
        prof["micr_code"] = col2.text_input("MICR Code", value=prof["micr_code"])
        
        if st.button("💾 Submit Proforma", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("proforma_branch", st.session_state.get("username", "USER"), prof, subject=f"Proforma: {prof['branch_name']}")
                st.success("Branch proforma saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["prof_step"] > 1:
        if c1.button("⬅️ Previous", key="prof_prev"):
            st.session_state["prof_step"] -= 1
            st.rerun()
    if st.session_state["prof_step"] < 3:
        if c2.button("Next ➡️", key="prof_next"):
            st.session_state["prof_step"] += 1
            st.rerun()

def render_reversal_charges_wizard() -> None:
    st.markdown("### 🔄 Reversal of Charges Wizard")
    if "rev_step" not in st.session_state: st.session_state["rev_step"] = 1
    if "rev_data" not in st.session_state:
        st.session_state["rev_data"] = {
            "customer_name": "", "account_no": "", "cif_id": "",
            "charge_type": "SMS Charges", "charge_date": datetime.date.today(), "amount": 0.0,
            "reversal_amount": 0.0, "reason": "Bank Error", "justification": ""
        }
    
    rev = st.session_state["rev_data"]
    
    if st.session_state["rev_step"] == 1:
        st.markdown("#### Step 1: Customer Details")
        col1, col2 = st.columns(2)
        rev["customer_name"] = col1.text_input("Customer Name", value=rev["customer_name"])
        rev["cif_id"] = col2.text_input("CIF ID / Customer ID", value=rev["cif_id"])
        rev["account_no"] = st.text_input("Account Number", value=rev["account_no"])
        
    elif st.session_state["rev_step"] == 2:
        st.markdown("#### Step 2: Charge Details")
        col1, col2 = st.columns(2)
        rev["charge_type"] = col1.selectbox("Charge Type", ["SMS Charges", "LRS (Ledger Folio)", "AMC Charges", "Cheque Return", "Stop Payment", "Processing Fee", "Penalty Interest", "Other"])
        rev["charge_date"] = col2.date_input("Date of Original Charge", value=rev["charge_date"])
        rev["amount"] = col1.number_input("Original Amount Charged (₹)", value=rev["amount"])
        
    elif st.session_state["rev_step"] == 3:
        st.markdown("#### Step 3: Reversal & Justification")
        col1, col2 = st.columns(2)
        rev["reversal_amount"] = col1.number_input("Amount to be Reversed (₹)", value=rev["reversal_amount"])
        rev["reason"] = col2.selectbox("Reason for Reversal", ["Bank Error", "System Error", "Customer Request (First Time)", "Customer Goodwill", "Fee Waiver Approved by RO", "Other"])
        rev["justification"] = st.text_area("Detailed Justification", value=rev["justification"])
        
        if st.button("💾 Submit Reversal Request", use_container_width=True):
            with get_db_session() as session:
                svc = WizardService(session)
                sub = svc.save_submission("reversal_charges", st.session_state.get("username", "USER"), rev, subject=f"Reversal: {rev['account_no']} - ₹{rev['reversal_amount']}")
                st.success("Reversal request saved to archive!")

    # Nav
    st.divider()
    c1, c2 = st.columns(2)
    if st.session_state["rev_step"] > 1:
        if c1.button("⬅️ Previous", key="rev_prev"):
            st.session_state["rev_step"] -= 1
            st.rerun()
    if st.session_state["rev_step"] < 3:
        if c2.button("Next ➡️", key="rev_next"):
            st.session_state["rev_step"] += 1
            st.rerun()

def render_office_note_wizard() -> None:
    from src.interface.streamlit.pages.execution import render_office_note_tab
    render_office_note_tab(DocumentService(), get_master_service)
def render_document_archive() -> None:
    st.markdown("### 🗄️ Unified Document Archive")
    st.caption("Centralized list of all generated documents, wizards, and returns.")
    
    with get_db_session() as session:
        svc = WizardService(session)
        submissions = svc.get_submissions()
        
        if not submissions:
            st.info("No documents found in the archive.")
            return
            
        data = []
        for s in submissions:
            content = json.loads(s.content_json)
            data.append({
                "ID": s.id,
                "Type": s.wizard_type.replace('_', ' ').title(),
                "Subject": s.subject or "N/A",
                "Reference": s.reference_no or "N/A",
                "Submitted By": s.submitted_by,
                "Date": s.created_at.strftime("%d.%m.%Y %H:%M"),
                "_raw": content
            })
            
        df = pd.DataFrame(data)
        
        # Search/Filter
        search = st.text_input("🔍 Search documents by Subject or Reference", "")
        if search:
            df = df[df["Subject"].str.contains(search, case=False) | df["Reference"].str.contains(search, case=False)]
            
        for i, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{row['Type']}**: {row['Subject']}")
                    st.caption(f"Ref: {row['Reference']} | Submitted by: {row['Submitted By']} on {row['Date']}")
                
                with c2:
                    c2_1, c2_2 = st.columns(2)
                    if c2_1.button("📄 PDF", key=f"gen_pdf_{row['ID']}"):
                        with st.spinner("Generating..."):
                            doc_svc = DocumentService()
                            pdf = doc_svc.generate_wizard_pdf(
                                wizard_type=row['Type'].lower().replace(' ', '_'),
                                data=row['_raw'],
                                submitted_by=row['Submitted By'],
                                subject=row['Subject'],
                                ref=row['Reference']
                            )
                            st.session_state[f"pdf_preview_{row['ID']}"] = pdf
                    
                    if c2_2.button("✏️ Edit", key=f"edit_{row['ID']}"):
                        # Load data into session state
                        wiz_id = row['Type'].lower().replace(' ', '_')
                        st.session_state["wizard_selection"] = wiz_id
                        # Map to specific data keys
                        data_key_map = {
                            "broken_interest": "wiz_data",
                            "expense_approval": "exp_data",
                            "gl_activation": "gl_data",
                            "rbi_proforma": "rbi_data",
                            "high_value_dd": "dd_data",
                            "micr_request": "micr_data"
                        }
                        key = data_key_map.get(wiz_id)
                        if key:
                            st.session_state[key] = row['_raw']
                            st.session_state[key.replace('data', 'step')] = 1
                        st.session_state["active_tab"] = "🏗️ Active Wizards"
                        st.rerun()
                
                with c3:
                    if st.button("🗑️ Delete", key=f"del_{row['ID']}"):
                        if svc.delete_submission(row['ID']):
                            st.success("Deleted.")
                            st.rerun()

                if f"pdf_preview_{row['ID']}" in st.session_state:
                    st.download_button(
                        "📥 Download PDF",
                        data=st.session_state[f"pdf_preview_{row['ID']}"],
                        file_name=f"Document_{row['ID'][:8]}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{row['ID']}"
                    )
                    if st.button("Close Preview", key=f"close_{row['ID']}"):
                        del st.session_state[f"pdf_preview_{row['ID']}"]
                        st.rerun()

def render_high_value_dd_wizard() -> None:
    # This was a duplicate or misaligned, the real one is defined above.
    pass

def render_circular_drafter_wizard() -> None:
    from src.interface.streamlit.pages.execution import render_circular_management_tab
    render_circular_management_tab(CircularService(), DocumentService())

def render_anniversary_note_wizard() -> None:
    st.markdown("### 🎂 Branch Anniversary Note")
    doc_service = DocumentService()
    with st.form("anniversary_note_form_wiz"):
        col1, col2 = st.columns(2)
        with col1:
            br_name = st.text_input("Branch Name")
            br_code = st.text_input("Branch SOL Code")
        with col2:
            f_date = st.text_input("Foundation Date")
            years = st.number_input("Anniversary Year", min_value=1, value=50)
        if st.form_submit_button("Generate Anniversary Note"):
            html_anniv = doc_service.generate_anniversary_note(branch_name=br_name, branch_code=br_code, foundation_date=f_date, years=int(years), prepared_by=st.session_state.get("username", "Staff User"))
            st.session_state["preview_note_anniv"] = html_anniv
    if "preview_note_anniv" in st.session_state:
        st.components.v1.html(st.session_state["preview_note_anniv"], height=400, scrolling=True)

def render_mail_merge_wizard() -> None:
    from src.interface.streamlit.pages.execution import render_mail_merge_tab
    render_mail_merge_tab(MailMergeService())
