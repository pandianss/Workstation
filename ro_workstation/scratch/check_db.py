import sqlite3
import json

def check_staff():
    conn = sqlite3.connect('data/mis_store.db')
    c = conn.cursor()
    c.execute('SELECT * FROM masters WHERE category="STAFF" AND code="63039"')
    row = c.fetchone()
    print(f"Staff 63039: {row}")
    
    # Check for Region Head in RO record
    c.execute('SELECT * FROM masters WHERE category="UNIT" AND metadata_json LIKE "%REGIONAL OFFICE%"')
    ro = c.fetchone()
    print(f"RO Record: {ro}")

if __name__ == "__main__":
    check_staff()
