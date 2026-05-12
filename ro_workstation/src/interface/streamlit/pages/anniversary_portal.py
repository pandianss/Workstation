from __future__ import annotations
import streamlit as st
import pandas as pd
import datetime
from src.application.services.anniversary_service import AnniversaryService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table
from src.interface.streamlit.state.services import get_doc_service_v2

def render() -> None:
    render_action_bar("Anniversary Portal", ["Founding Days", "Poster Generator", "Celebrations"])
    
    anniv_svc = AnniversaryService()
    doc_service = get_doc_service_v2()
    
    tab1, tab2, tab3 = st.tabs(["🎈 Branch Foundings", "👨‍💼 Staff Milestones", "📁 Founding Registry"])
    
    with tab1:
        st.markdown("### 📅 Branch Celebrations in the Next 30 Days")
        upcoming = anniv_svc.get_upcoming_anniversaries(days=30)
        
        if upcoming:
            for anniv in upcoming:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"#### {anniv['name']}")
                        st.caption(f"SOL: {anniv['sol']}")
                    with c2:
                        days_txt = "🎉 TODAY" if anniv["days_to_go"] == 0 else f"In {anniv['days_to_go']} days"
                        st.markdown(f"**{anniv['anniversary_date'].strftime('%d %B %Y')}**")
                        st.markdown(f":blue[{days_txt}] | Celebrating **{anniv['years']} Years**")
                    with c3:
                        if st.button("🎨 Poster", key=f"portal_post_{anniv['sol']}"):
                            with st.spinner("Generating..."):
                                html = doc_service.generate_anniversary_poster_html(anniv["name"], anniv["years"], anniv["open_date"].strftime("%d.%m.%Y"))
                                st.session_state[f"portal_post_html_{anniv['sol']}"] = html
                        
                if f"portal_post_html_{anniv['sol']}" in st.session_state:
                    with st.expander("👁️ Poster Preview & Image Download", expanded=True):
                        st.components.v1.html(st.session_state[f"portal_post_html_{anniv['sol']}"], height=800, scrolling=True)
                        st.info("💡 Use the blue button inside the preview above to download the high-res PNG.")
        else:
            st.info("No branch anniversaries found in the next 30 days.")

    with tab2:
        st.markdown("### 👨‍💼 Upcoming Staff Birthdays & Retirements")
        st.caption("Celebrating the life events of our regional team members.")
        
        lookahead = st.slider("Lookahead (Days)", 1, 60, 15)
        staff_celebs = anniv_svc.get_staff_celebrations(days=lookahead)
        
        if staff_celebs:
            for celeb in staff_celebs:
                icon = "🎂" if celeb["type"] == "BIRTHDAY" else "🌅"
                color = "green" if celeb["type"] == "BIRTHDAY" else "orange"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"#### {celeb['name']}")
                        st.markdown(f":{color}[{icon} {celeb['type']}] | {celeb['designation']}")
                    with c2:
                        days_txt = "🎉 TODAY" if celeb["days_to_go"] == 0 else f"In {celeb['days_to_go']} days"
                        st.markdown(f"**{celeb['date'].strftime('%d %B')}**")
                        st.markdown(f":blue[{days_txt}]")
                    with c3:
                        if st.button("🎨 Create Poster", key=f"staff_post_{celeb['roll']}_{celeb['type']}"):
                            with st.spinner("Rendering..."):
                                html = doc_service.generate_staff_milestone_html(celeb["roll"], celeb["type"])
                                st.session_state[f"staff_post_html_{celeb['roll']}"] = html
                
                if f"staff_post_html_{celeb['roll']}" in st.session_state:
                    with st.expander("👁️ Milestone Poster Preview", expanded=True):
                        st.components.v1.html(st.session_state[f"staff_post_html_{celeb['roll']}"], height=800, scrolling=True)
                        st.info("💡 Use the download button inside the preview above.")
        else:
            st.info(f"No staff milestones found in the next {lookahead} days.")

    with tab3:
        st.markdown("### 📋 Founding Registry")
        from src.interface.streamlit.state.services import get_master_service
        master_svc = get_master_service()
        units = master_svc.get_units_frame()
        
        # Filter only branches and those with open dates
        branches = units[units["Open Date"] != "N/A"].copy()
        
        if not branches.empty:
            # Add 'Month' column for sorting/filtering
            branches["Month"] = pd.to_datetime(branches["Open Date"], errors='coerce').dt.strftime('%B')
            
            selected_month = st.selectbox("Filter by Month", ["All"] + sorted(branches["Month"].unique().tolist(), key=lambda x: datetime.datetime.strptime(x, '%B').month))
            
            display_df = branches.copy()
            if selected_month != "All":
                display_df = display_df[display_df["Month"] == selected_month]
            
            render_data_table(display_df[["Code", "Name", "Open Date", "District", "Type"]], "Branch Founding Dates", "branch_anniversaries.xlsx")
            
            st.markdown("---")
            st.markdown("#### ⚡ Batch Poster Generation")
            st.caption("Generate a poster for any branch regardless of date.")
            
            col_b, col_y, col_a = st.columns([3, 1, 1])
            with col_b:
                target_branch = st.selectbox("Select Branch", display_df["Name"].tolist())
            with col_y:
                # Calculate years automatically for selected
                row = display_df[display_df["Name"] == target_branch].iloc[0]
                auto_years = anniv_svc.calculate_years(row["Open Date"])
                years = st.number_input("Years", min_value=1, value=auto_years)
            with col_a:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Generate Poster", use_container_width=True, key="batch_gen_btn"):
                    with st.spinner("Generating..."):
                        html = doc_service.generate_anniversary_poster_html(target_branch, years, row["Open Date"])
                        st.session_state["portal_batch_poster_html"] = html
            
            if "portal_batch_poster_html" in st.session_state:
                with st.expander("👁️ Poster Preview & Image Download", expanded=True):
                    st.components.v1.html(st.session_state["portal_batch_poster_html"], height=800, scrolling=True)
                    st.info("💡 Use the blue button inside the preview above to download the high-res PNG.")
        else:
            st.warning("No unit data with founding dates found. Please ensure branches.csv is synced.")
