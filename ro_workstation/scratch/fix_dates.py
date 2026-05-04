import sqlite3
import os

db_path = "data/mis_store.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update open_dt to remove time component if it exists
    cursor.execute("UPDATE advances_records SET open_dt = DATE(open_dt) WHERE open_dt LIKE '% %'")
    print(f"Fixed {cursor.rowcount} records in advances_records")
    
    conn.commit()
    conn.close()
