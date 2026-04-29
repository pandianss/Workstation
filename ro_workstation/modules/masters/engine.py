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
            ("DEPARTMENT", "CRMD", "Credit Risk Management Dept", "क्रेडिट जोखिम प्रबंधन विभाग", "கடன் ஆபத்து மேலாண்மை"),
            ("DEPARTMENT", "HRDD", "Human Resources Dept", "मानव संसाधन विभाग", "மனித வளத் துறை"),
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
