import sys
import os
import json

# Add current directory to path
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

BRANCHES = [
    ("3933", "Regional Office Dindigul", "क्षेत्रीय कार्यालय डिंडीगुल", "மண்டல அலுவலகம் திண்டுக்கல்", {"SOL": "3933", "Type": "RO"}),
    ("0001", "Dindigul Main", "डिंडीगुल मेन", "திண்டுக்கல் பிரதான", {"SOL": "0001", "Type": "Branch"}),
    ("0002", "Palani", "पलानी", "பழனி", {"SOL": "0002", "Type": "Branch"}),
    ("0003", "Oddanchatram", "ओड्डनचत्रम", "ஒட்டன்சத்திரம்", {"SOL": "0003", "Type": "Branch"}),
    ("0004", "Vedasandur", "वेदासंदूर", "வேதசந்தூர்", {"SOL": "0004", "Type": "Branch"}),
    ("0005", "Natham", "नथम", "நத்தம்", {"SOL": "0005", "Type": "Branch"}),
    ("0006", "Nilakottai", "निलकोट्टई", "நிலக்கோட்டை", {"SOL": "0006", "Type": "Branch"}),
    ("0007", "Batlagundu", "बतलागुंडु", "வத்தலகுண்டு", {"SOL": "0007", "Type": "Branch"}),
    ("0008", "Kodaikanal", "कोडैकनाल", "கொடைக்கானல்", {"SOL": "0008", "Type": "Branch"}),
    ("0009", "Athoor", "अतूर", "ஆத்தூர்", {"SOL": "0009", "Type": "Branch"}),
    ("0010", "Guziliamparai", "गुज़िलियमपाराई", "குஜிலியம்பாறை", {"SOL": "0010", "Type": "Branch"}),
]

STAFF = [
    ("63039", "S. Pandian", "एस. पांडियन", "எஸ். பாண்டியன்", {"SOL": "3933", "Designation": "Regional Manager", "Grade": "TEGS-VI"}),
    ("63040", "M. Rajan", "एम. राजन", "எம். ராஜன்", {"SOL": "3933", "Designation": "Chief Manager", "Grade": "SMGS-IV"}),
    ("63041", "A. Kumar", "ए. कुमार", "ஏ. குமார்", {"SOL": "3933", "Designation": "Senior Manager", "Grade": "MMGS-III"}),
    ("63042", "R. Priya", "आर. प्रिया", "ஆர். பிரியா", {"SOL": "0001", "Designation": "Branch Manager", "Grade": "MMGS-III"}),
    ("63043", "K. Selvam", "के. सेल्वम", "கே. செல்வம்", {"SOL": "0002", "Designation": "Branch Manager", "Grade": "MMGS-II"}),
]

def seed_all():
    session = Session()
    
    # 1. Departments
    for code, en, hi, loc in DEPT_DATA:
        existing = session.query(MasterRecord).filter(MasterRecord.category == "DEPARTMENT", MasterRecord.code == code).first()
        if not existing:
            session.add(MasterRecord(category="DEPARTMENT", code=code, name_en=en, name_hi=hi, name_local=loc))
    
    # 2. Branches
    for code, en, hi, loc, meta in BRANCHES:
        existing = session.query(MasterRecord).filter(MasterRecord.category == "BRANCH", MasterRecord.code == code).first()
        if not existing:
            session.add(MasterRecord(category="BRANCH", code=code, name_en=en, name_hi=hi, name_local=loc, metadata_json=json.dumps(meta)))
            
    # 3. Staff
    for code, en, hi, loc, meta in STAFF:
        existing = session.query(MasterRecord).filter(MasterRecord.category == "STAFF", MasterRecord.code == code).first()
        if not existing:
            session.add(MasterRecord(category="STAFF", code=code, name_en=en, name_hi=hi, name_local=loc, metadata_json=json.dumps(meta)))

    session.commit()
    session.close()
    print("Master Data seeding completed successfully.")

if __name__ == "__main__":
    seed_all()
