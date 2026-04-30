import datetime
import json
import streamlit as st
from modules.masters.engine import get_master_records

def render_birthday_alerts():
    staff_records = get_master_records("STAFF")
    today = datetime.date.today()
    
    birthdays_today = []
    upcoming_birthdays = []
    
    for s in staff_records:
        if s.metadata_json:
            try:
                meta = json.loads(s.metadata_json)
                dob_str = meta.get("dob")
                if dob_str:
                    dob = datetime.date.fromisoformat(dob_str)
                    
                    # Check if today is birthday
                    if dob.month == today.month and dob.day == today.day:
                        birthdays_today.append({
                            "name": s.name_en,
                            "code": s.code,
                            "age": today.year - dob.year
                        })
                    # Check if upcoming (next 7 days)
                    # We create a date for this year's birthday
                    try:
                        this_year_bday = datetime.date(today.year, dob.month, dob.day)
                        if today < this_year_bday <= today + datetime.timedelta(days=7):
                            upcoming_birthdays.append({
                                "name": s.name_en,
                                "date": this_year_bday,
                                "days_left": (this_year_bday - today).days
                            })
                    except ValueError:
                        # Handle Feb 29
                        pass
            except:
                continue

    if birthdays_today:
        st.balloons()
        for b in birthdays_today:
            st.markdown(
                f"""
                <div class="glass-panel" style="border-left: 5px solid #FF4B4B; background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(255,255,255,0) 100%);">
                    <div style="font-size: 1.5rem;">🎂 Happy Birthday, <strong>{b['name']}</strong>!</div>
                    <div style="color: #666;">Wishing you a wonderful day from the Regional Office Team.</div>
                </div>
                <div class="divider-space"></div>
                """,
                unsafe_allow_html=True
            )

    if upcoming_birthdays:
        with st.sidebar.expander("🎂 Upcoming Birthdays", expanded=True):
            for ub in sorted(upcoming_birthdays, key=lambda x: x["date"]):
                st.write(f"**{ub['date'].strftime('%d %b')}**: {ub['name']}")
