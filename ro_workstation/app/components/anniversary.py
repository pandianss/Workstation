import streamlit as st
from app.services.anniversary_service import get_upcoming_anniversaries, get_congratulations_message
from app.services.report_service import generate_ro_anniversary_letter

def render_anniversary_alerts():
    upcoming = get_upcoming_anniversaries(days=30)
    
    if not upcoming:
        return
        
    st.markdown("### 🎊 Branch Anniversaries & Campaigns")
    
    # Highlight Today
    todays = [a for a in upcoming if a['is_today']]
    for a in todays:
        st.success(get_congratulations_message(a))
        st.balloons()
        # Allow downloading the RO Letter even on the day
        letter_pdf = generate_ro_anniversary_letter(a)
        st.download_button(
            label=f"📜 Download RO Congratulatory Letter for {a['name']}",
            data=letter_pdf,
            file_name=f"RO_Letter_{a['code']}_{a['anniversary_date'].year}.pdf",
            mime="application/pdf",
            key=f"dl_{a['code']}"
        )
            
    # Campaigns & Upcoming
    future = [a for a in upcoming if not a['is_today']]
    if future:
        for a in future:
            if a['is_campaign_period']:
                st.info(f"🚀 **{a['name']}** ({a['code']}) is in its **Special Business Fortnight** drive! (Foundation Day: {a['anniversary_date'].strftime('%d %B')})")
                col1, col2 = st.columns([3, 1])
                col1.write(f"The **{a['name']}** branch is currently running special campaigns leading up to its **{a['years']}th Anniversary**.")
                
                letter_pdf = generate_ro_anniversary_letter(a)
                col2.download_button(
                    label="📜 RO Letter",
                    data=letter_pdf,
                    file_name=f"RO_Letter_{a['code']}.pdf",
                    mime="application/pdf",
                    key=f"cp_{a['code']}"
                )
            
        with st.expander("Other Upcoming Anniversaries", expanded=False):
            for a in [f for f in future if not f['is_campaign_period']]:
                import datetime
                days_left = (a['anniversary_date'] - datetime.date.today()).days
                st.write(f"📅 **{a['anniversary_date'].strftime('%d %B')}**: **{a['name']}** ({a['years']} Years) — *In {days_left} days*")
