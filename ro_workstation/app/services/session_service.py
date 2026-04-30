import json
import os
from datetime import datetime, timedelta
from modules.utils.paths import project_path

SESSION_FILE = project_path("app", "data", "sessions.json")

def ensure_file():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def start_session(pc_username):
    ensure_file()
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data[pc_username] = datetime.now().isoformat()
    
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def end_session(pc_username):
    ensure_file()
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if pc_username in data:
        del data[pc_username]
    
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_session_active(pc_username, timeout_hours=4):
    ensure_file()
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if pc_username in data:
        start_time = datetime.fromisoformat(data[pc_username])
        if datetime.now() - start_time < timedelta(hours=timeout_hours):
            return True
        else:
            # Cleanup expired session
            end_session(pc_username)
            
    return False
