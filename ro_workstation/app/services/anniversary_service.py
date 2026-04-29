import json
from datetime import datetime, date, timedelta
from modules.masters.engine import get_master_records

def get_upcoming_anniversaries(days=30):
    branches = get_master_records(category="BRANCH")
    today = date.today()
    upcoming = []
    
    for b in branches:
        if not b.metadata_json:
            continue
            
        try:
            meta = json.loads(b.metadata_json)
            open_date_str = meta.get("openDate")
            if not open_date_str or str(open_date_str).lower() == 'nan':
                continue
                
            # Parse openDate (YYYY-MM-DD)
            open_date = datetime.strptime(open_date_str, "%Y-%m-%d").date()
            
            # Calculate this year's anniversary
            this_year_anniversary = date(today.year, open_date.month, open_date.day)
            
            # If it already passed this year, look at next year (though user only asked for next 30 days)
            # But for "next 30 days" check, we might cross year boundary (Dec -> Jan)
            
            # Simple check: is this_year_anniversary between today and today + days?
            # Or if today is late Dec, check next_year_anniversary too.
            
            next_30_days = [today + timedelta(days=i) for i in range(days + 1)]
            
            # Check if any day in the next 30 days matches month/day
            for d in next_30_days:
                if d.month == open_date.month and d.day == open_date.day:
                    years = d.year - open_date.year
                    days_until = (d - today).days
                    
                    upcoming.append({
                        "code": b.code,
                        "name": b.name_en,
                        "open_date": open_date,
                        "anniversary_date": d,
                        "years": years,
                        "is_today": (d == today),
                        "is_campaign_period": (0 < days_until <= 14),
                        "days_until": days_until
                    })
                    break
        except Exception:
            continue
            
    # Sort by anniversary date
    upcoming.sort(key=lambda x: x["anniversary_date"])
    return upcoming

def get_congratulations_message(anniversary):
    name = anniversary['name']
    years = anniversary['years']
    ordinal = {1: 'st', 2: 'nd', 3: 'rd'}.get(years % 10 if years % 100 not in [11, 12, 13] else 0, 'th')
    
    messages = [
        f"🎊 Congratulations to **{name}** branch on completing **{years}{ordinal}** year of service! 🎊",
        f"🚀 Happy Foundation Day to the team at **{name}**! Celebrating **{years} years** of excellence.",
        f"🎂 **{name}** branch was opened on this day in {anniversary['open_date'].year}. Cheers to {years} years!"
    ]
    
    import random
    return random.choice(messages)
