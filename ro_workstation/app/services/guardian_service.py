import json
import os
from datetime import datetime
from modules.utils.paths import project_path

FOLLOWUP_FILE = project_path("app", "data", "guardian_followups.json")

def ensure_file():
    if not os.path.exists(FOLLOWUP_FILE):
        with open(FOLLOWUP_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def record_followup(go_username, sol, details):
    ensure_file()
    with open(FOLLOWUP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data.append({
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "go_username": go_username,
        "sol": sol,
        "details": details
    })
    
    with open(FOLLOWUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return True

def get_followups(sol=None, go_username=None):
    ensure_file()
    with open(FOLLOWUP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if sol:
        data = [x for x in data if x["sol"] == sol]
    if go_username:
        data = [x for x in data if x["go_username"] == go_username]
        
    return data
