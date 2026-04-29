from sqlalchemy import Column, String, Date, Time, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    dept = Column(String)
    task_type = Column(String)
    priority = Column(String)
    due_date = Column(Date)
    due_time = Column(Time, nullable=True)
    assigned_to = Column(String)
    assigned_by = Column(String, nullable=True)
    status = Column(String, default="OPEN")
    source = Column(String)
    linked_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    snoozed_until = Column(Date, nullable=True)
    recurrence = Column(String, nullable=True)

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String)
    remind_at = Column(DateTime)
    channel = Column(String)
    sent = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)
