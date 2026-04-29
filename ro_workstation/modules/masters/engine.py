import json
from pathlib import Path
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from .models import Base, MasterRecord
from ..utils.paths import project_path

DEFAULT_DB_PATH = project_path("data", "ro_tasks.db")
FALLBACK_DB_PATH = Path(tempfile.gettempdir()) / "ro_workstation" / "ro_tasks.db"

def _initialize_engine():
    for candidate in (DEFAULT_DB_PATH, FALLBACK_DB_PATH):
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate_engine = create_engine(f"sqlite:///{candidate.as_posix()}")
            Base.metadata.create_all(candidate_engine)
            return candidate_engine, candidate
        except OperationalError:
            continue

    memory_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(memory_engine)
    return memory_engine, Path(":memory:")

engine, ACTIVE_DB_PATH = _initialize_engine()
Session = sessionmaker(bind=engine)

def get_master_records(category=None, active_only=False):
    session = Session()
    query = session.query(MasterRecord)
    if category:
        query = query.filter(MasterRecord.category == category)
    if active_only:
        query = query.filter(MasterRecord.is_active == True)
    records = query.order_by(MasterRecord.code).all()
    session.close()
    return records

def create_master_record(category, code, name_en, name_hi="", name_local="", metadata_dict=None):
    session = Session()
    # Check if code exists in category
    existing = session.query(MasterRecord).filter(
        MasterRecord.category == category, 
        MasterRecord.code == code
    ).first()
    
    if existing:
        session.close()
        raise ValueError(f"Record with code '{code}' already exists in category '{category}'")
        
    metadata_json = json.dumps(metadata_dict) if metadata_dict else None
    
    new_record = MasterRecord(
        category=category,
        code=code,
        name_en=name_en,
        name_hi=name_hi,
        name_local=name_local,
        metadata_json=metadata_json
    )
    session.add(new_record)
    session.commit()
    session.refresh(new_record)
    session.close()
    return new_record

def update_master_record(record_id, **kwargs):
    session = Session()
    record = session.query(MasterRecord).filter(MasterRecord.id == record_id).first()
    if not record:
        session.close()
        return False
        
    for key, value in kwargs.items():
        if hasattr(record, key):
            setattr(record, key, value)
            
    if 'metadata_dict' in kwargs:
        record.metadata_json = json.dumps(kwargs['metadata_dict'])
        
    session.commit()
    session.close()
    return True

def delete_master_record(record_id):
    session = Session()
    record = session.query(MasterRecord).filter(MasterRecord.id == record_id).first()
    if record:
        session.delete(record)
        session.commit()
        session.close()
        return True
    session.close()
    return False

def init_default_masters():
    """Populate some default categories if empty."""
    session = Session()
    count = session.query(MasterRecord).count()
    if count == 0:
        defaults = [
            ("DEPARTMENT", "FI", "Financial Inclusion", "वित्तीय समावेशन", "நிதி உள்ளடக்கம்"),
            ("DEPARTMENT", "CRMD", "Credit Monitoring", "क्रेडिट निगरानी", "கடன் கண்காணிப்பு"),
            ("DEPARTMENT", "PLAN", "Planning", "योजना विभाग", "திட்டமிடல்"),
            ("DEPARTMENT", "ARID", "Agriculture & Rural Infra Dev", "कृषि एवं ग्रामीण विकास", "வேளாண்மை மற்றும் ஊரக வளர்ச்சி"),
            ("DEPARTMENT", "HRDD", "Human Resources", "मानव संसाधन", "மனித வள மேம்பாடு"),
            ("DEPARTMENT", "GAD", "General Administration", "सामान्य प्रशासन", "பொदु நிர்வாகம்"),
            ("DEPARTMENT", "COM", "Compliance", "अनुपालन विभाग", "இணக்கத் துறை"),
            ("DEPARTMENT", "MKT", "Marketing", "विपणन विभाग", "சந்தைப்படுத்தல்"),
            ("DEPARTMENT", "LAW", "Law Department", "विधि विभाग", "சட்டத் துறை"),
            ("DEPARTMENT", "INS", "Inspection", "निरीक्षण विभाग", "ஆய்வுத் துறை"),
            ("DEPARTMENT", "RSK", "Risk Management", "जोखिम प्रबंधन", "இடர் மேலாண்மை"),
            ("DEPARTMENT", "SME", "MSME Division", "एमएसएमई प्रभाग", "சிறு, குறு மற்றும் நடுத்தர தொழில்"),
            ("DEPARTMENT", "RET", "Retail Department", "खुदरा विभाग", "சில்லறை வணிகம்"),
            ("DEPARTMENT", "RCC", "Regional Computer Centre", "क्षेत्रीय कंप्यूटर केंद्र", "மண்டல கணினி மையம்"),
            ("BRANCH", "B001", "Dindigul Main", "डिंडीगुल मेन", "திண்டுக்கல் பிரதான"),
            ("BRANCH", "B002", "Palani", "पलानी", "பழனி"),
            ("USER_ROLE", "RO_ADMIN", "Regional Office Admin", "क्षेत्रीय कार्यालय व्यवस्थापक", "மண்டல அலுவலக நிர்வாகி"),
        ]
        for cat, code, en, hi, loc in defaults:
            record = MasterRecord(category=cat, code=code, name_en=en, name_hi=hi, name_local=loc)
            session.add(record)
        session.commit()
    session.close()

# Auto-initialize defaults on import if empty
init_default_masters()
