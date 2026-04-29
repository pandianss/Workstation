from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import uuid
import os
import json

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    ip_address = Column(String, default="127.0.0.1")

os.makedirs("data", exist_ok=True)
db_path = os.path.join("data", "ro_audit.db")
engine = create_engine(f"sqlite:///{db_path}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def log_action(user_id, action, entity_type, entity_id, old_value=None, new_value=None):
    session = Session()
    old_val_str = json.dumps(old_value) if old_value else None
    new_val_str = json.dumps(new_value) if new_value else None
    
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_val_str,
        new_value=new_val_str
    )
    session.add(log)
    session.commit()
    session.close()

def get_logs(limit=100):
    session = Session()
    logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    session.close()
    return logs
