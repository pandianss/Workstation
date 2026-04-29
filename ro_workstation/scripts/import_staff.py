import sys
import os
import json
import pandas as pd

# Add current directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.masters.engine import Session, MasterRecord

def seed_from_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    session = Session()
    count = 0
    
    for _, row in df.iterrows():
        code = str(row['Roll'])
        name = row['Name']
        designation = row['Designation']
        grade = row['Grade']
        sol = str(row['SOL'])
        
        existing = session.query(MasterRecord).filter(
            MasterRecord.category == "STAFF",
            MasterRecord.code == code
        ).first()
        
        meta = {
            "SOL": sol,
            "Designation": designation,
            "Grade": grade
        }
        
        if existing:
            existing.name_en = name
            existing.metadata_json = json.dumps(meta)
        else:
            new_staff = MasterRecord(
                category="STAFF",
                code=code,
                name_en=name,
                name_hi="", # Could be added later
                name_local="",
                metadata_json=json.dumps(meta),
                is_active=True
            )
            session.add(new_staff)
            count += 1
            
    session.commit()
    session.close()
    print(f"Successfully imported {count} staff members from CSV.")

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "../../Staff2.csv")
    seed_from_csv(csv_file)
