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


def update_user_access(username, role=None, depts=None):
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for user in data:
        if user["username"] == username:
            if role is not None:
                user["role"] = role
            if depts is not None:
                user["depts"] = depts
            updated = True
            break

    if updated:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return updated


def update_user_guardian_branches(username, assigned_branches):
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for user in data:
        if user["username"] == username:
            user["assigned_branches"] = assigned_branches
            updated = True
            break

    if updated:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return updated
def sync_ro_staff_as_users(staff_records):
    """
    Automatically authorizes all RO staff (SOL 3933) as system users.
    Assigns hierarchical rankings and supports multi-department mapping.
    """
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)
    
    existing_usernames = {u["username"] for u in data}
    new_users_added = 0

    for s in staff_records:
        if s.code not in existing_usernames:
            meta = json.loads(s.metadata_json)
            designation = meta.get("Designation", "").upper()
            grade = meta.get("Grade", "").upper()
            
            # 1. Determine Hierarchy Rank (Lower is Higher)
            # Rank 1: Head (SRM/CRM)
            # Rank 2: 2nd Line (Deputy/Chief Manager II line)
            # Rank 3: Dept Heads (Chief/Senior Managers)
            # Rank 4: Desk Officers (Managers/Asst Managers)
            
            rank = 4 # Default
            if "REGIONAL MANAGER" in designation:
                rank = 1
            elif "II LINE" in designation or "DEPUTY" in designation:
                rank = 2
            elif any(x in designation for x in ["CHIEF MANAGER", "SENIOR MANAGER"]):
                rank = 3
            elif any(x in designation for x in ["MANAGER", "ASST MANAGER"]):
                rank = 4

            # 2. Determine Role
            if rank <= 2: role = "ADMIN"
            elif rank == 3: role = "MANAGER"
            else: role = "USER"
            
            data.append({
                "username": s.code,
                "name": s.name_en,
                "role": role,
                "depts": ["3933"], # Initialize with SOL, can be expanded to multiple depts
                "rank": rank,
                "designation": meta.get("Designation", "Staff"),
                "grade": grade
            })
            new_users_added += 1

    # Save and return
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return new_users_added

def get_sorted_users():
    """
    Returns users sorted by hierarchy rank, with names/ranks 
    dynamically synced from Master Data.
    """
    with open(USER_FILE, encoding="utf-8") as f:
        data = json.load(f)
    
    # Fetch Master Staff records to get latest names/designations
    from modules.masters.engine import get_master_records
    staff_records = {s.code: s for s in get_master_records("STAFF")}
    
    # Enrich user data from Master Records
    for u in data:
        username = u["username"]
        if username in staff_records:
            s = staff_records[username]
            u["name"] = s.name_en # Always use latest from Master Data
            
            # Optionally update rank/designation from metadata if available
            try:
                meta = json.loads(s.metadata_json) if s.metadata_json else {}
                u["designation"] = meta.get("Designation", u.get("designation", "Staff"))
                u["grade"] = meta.get("Grade", u.get("grade", "N/A"))
            except:
                pass
        
        # Fallbacks for legacy/system users
        if "rank" not in u: u["rank"] = 4
        if "name" not in u: u["name"] = u.get("name", username)
        if "designation" not in u: u["designation"] = u.get("designation", "System User")
        if "grade" not in u: u["grade"] = u.get("grade", "N/A")
        if "depts" not in u: u["depts"] = [u.get("dept", "3933")]
    
    df = pd.DataFrame(data)
    
    # Ensure columns exist
    for col in ["username", "name", "designation", "role", "depts", "grade", "rank"]:
        if col not in df.columns:
            df[col] = None

    return df.sort_values(by="rank")
