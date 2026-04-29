import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
USER_FILE = DATA_DIR / "users.json"

if not USER_FILE.exists():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump([{"username": "admin", "role": "ADMIN", "dept": "ALL"}], f)


def get_users():
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    if "dept" not in df.columns:
        df["dept"] = "ALL"
    return df


def add_user(username, role, dept="ALL"):
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    data.append({
        "username": username,
        "role": role,
        "dept": dept or "ALL",
    })

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def update_role(username, role):
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    for user in data:
        if user["username"] == username:
            user["role"] = role

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
def sync_ro_staff_as_users(staff_records):
    """
    Automatically authorizes all RO staff (SOL 3933) as system users if not already present.
    """
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)
    
    existing_usernames = {u["username"] for u in data}
    new_users_added = 0

    for s in staff_records:
        if s.code not in existing_usernames:
            meta = json.loads(s.metadata_json)
            designation = meta.get("Designation", "").upper()
            
            # Logic: Chief Managers and above are ADMINs, Managers are MANAGERs, others are USERs
            if any(x in designation for x in ["REGIONAL", "CHIEF", "SENIOR"]):
                role = "MANAGER" # Defaulting to MANAGER for safety, can be upgraded manually
            else:
                role = "USER"
            
            data.append({
                "username": s.code,
                "role": role,
                "dept": "3933"
            })
            new_users_added += 1

    if new_users_added > 0:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    return new_users_added
