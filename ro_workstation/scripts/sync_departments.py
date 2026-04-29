import sys
import os
import yaml

# Add current directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.masters.engine import Session, MasterRecord

DEPT_DATA = [
    ("FI", "Financial Inclusion", "वित्तीय समावेशन", "நிதி உள்ளடக்கம்"),
    ("CRMD", "Credit Monitoring", "क्रेडिट निगरानी", "கடன் கண்காணிப்பு"),
    ("PLAN", "Planning", "योजना विभाग", "திட்டமிடல்"),
    ("ARID", "Agriculture & Rural Infra Dev", "कृषि एवं ग्रामीण विकास", "வேளாண்மை மற்றும் ஊரக வளர்ச்சி"),
    ("HRDD", "Human Resources", "मानव संसाधन", "மனித வள மேம்பாடு"),
    ("GAD", "General Administration", "सामान्य प्रशासन", "பொது நிர்வாகம்"),
    ("COM", "Compliance", "अनुपालन विभाग", "இணக்கத் துறை"),
    ("MKT", "Marketing", "विपणन विभाग", "சந்தைப்படுத்தல்"),
    ("LAW", "Law Department", "विधि विभाग", "சட்டத் துறை"),
    ("INS", "Inspection", "निरीक्षण विभाग", "ஆய்வுத் துறை"),
    ("RSK", "Risk Management", "जोखिम प्रबंधन", "இடர் மேலாண்மை"),
    ("SME", "MSME Division", "एमएसएमई प्रभाग", "சிறு, குறு மற்றும் நடுத்தர தொழில்"),
    ("RET", "Retail Department", "खुदरा विभाग", "சில்லறை வணிகம்"),
    ("RCC", "Regional Computer Centre", "क्षेत्रीय कंप्यूटर केंद्र", "மண்டல கணினி மையம்")
]

def sync_depts():
    session = Session()
    count_added = 0
    count_updated = 0
    
    for code, en, hi, loc in DEPT_DATA:
        existing = session.query(MasterRecord).filter(
            MasterRecord.category == "DEPARTMENT",
            MasterRecord.code == code
        ).first()
        
        if existing:
            existing.name_en = en
            existing.name_hi = hi
            existing.name_local = loc
            count_updated += 1
        else:
            new_dept = MasterRecord(
                category="DEPARTMENT",
                code=code,
                name_en=en,
                name_hi=hi,
                name_local=loc,
                is_active=True
            )
            session.add(new_dept)
            count_added += 1
            
    session.commit()
    session.close()
    print(f"Successfully synced departments: {count_added} added, {count_updated} updated.")

if __name__ == "__main__":
    sync_depts()
