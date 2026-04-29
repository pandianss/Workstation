import pandas as pd
from datetime import datetime
from modules.utils.paths import project_path

DATA_DIR = project_path("app", "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DATA_DIR / "audit.log"

def log_action(user, action):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {user} | {action}\n")

def get_audit_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame(columns=["Timestamp", "User", "Action"])
    
    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(" | ")
            if len(parts) == 3:
                logs.append({
                    "Timestamp": parts[0],
                    "User": parts[1],
                    "Action": parts[2]
                })
    
    df = pd.DataFrame(logs)
    if not df.empty:
        df = df.sort_values("Timestamp", ascending=False)
    return df
