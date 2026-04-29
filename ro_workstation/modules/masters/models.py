from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class MasterRecord(Base):
    __tablename__ = 'master_records'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, nullable=False) # e.g., 'DEPARTMENT', 'BRANCH', 'USER', 'ASSET_ATM'
    code = Column(String, nullable=False)     # e.g., 'IT', 'MUM-01'
    name_en = Column(String, nullable=False)  # English name
    name_hi = Column(String, nullable=True)   # Hindi name
    name_local = Column(String, nullable=True) # Regional language name
    is_active = Column(Boolean, default=True)
    metadata_json = Column(String, nullable=True) # Additional attributes like location, grade level
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
