from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Time, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class TaskModel(Base):
    __tablename__ = "tasks"

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


class ReminderModel(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String)
    remind_at = Column(DateTime)
    channel = Column(String)
    sent = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)


class MISRecordModel(Base):
    __tablename__ = "mis_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    sol = Column(Integer, nullable=False, index=True)
    sb = Column(Float, default=0.0)
    cd = Column(Float, default=0.0)
    td = Column(Float, default=0.0)
    bulk_dep = Column(Float, default=0.0)
    rec_q1 = Column(Float, default=0.0)
    rec_q2 = Column(Float, default=0.0)
    rec_q3 = Column(Float, default=0.0)
    rec_q4 = Column(Float, default=0.0)
    cash_on_hand = Column(Float, default=0.0)
    atm_cash = Column(Float, default=0.0)
    bc_cash = Column(Float, default=0.0)
    bna_cash = Column(Float, default=0.0)
    crl = Column(Float, default=0.0)
    pl = Column(Float, default=0.0)
    npa = Column(Float, default=0.0)
    core_agri = Column(Float, default=0.0)
    gold = Column(Float, default=0.0)
    msme = Column(Float, default=0.0)
    housing = Column(Float, default=0.0)
    vehicle = Column(Float, default=0.0)
    personal = Column(Float, default=0.0)
    mortgage = Column(Float, default=0.0)
    education = Column(Float, default=0.0)
    liquirent = Column(Float, default=0.0)
    other_retail = Column(Float, default=0.0)


class IngestedFileModel(Base):
    __tablename__ = "ingested_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class MasterRecordModel(Base):
    __tablename__ = "masters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    name_en = Column(String, nullable=False)
    name_hi = Column(String)
    name_local = Column(String)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(String)  # Store JSON as string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sol = Column(Integer, nullable=False, index=True)
    parameter = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    target = Column(Float, nullable=False)


class AdvancesRecordModel(Base):
    __tablename__ = "advances_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_dt = Column(Date, nullable=False, index=True)
    branch_code = Column(Integer, nullable=False, index=True)
    ac_name = Column(String)
    foracid = Column(String, index=True)
    schm_code = Column(String)
    gl_sub_cd = Column(String)
    open_dt = Column(Date)
    limit_cr = Column(Float)
    balance_cr = Column(Float)
    risk_category = Column(String, index=True)
    l1_category = Column(String)
    l2_sector = Column(String)
    l3_scheme = Column(String)
    priority_type = Column(String)

class MilestoneAchievementModel(Base):
    __tablename__ = 'milestone_achievements'
    
    id = Column(Integer, primary_key=True)
    sol = Column(Integer, nullable=False)
    branch_name = Column(String(100), nullable=False)
    parameter = Column(String(50), nullable=False)
    milestone = Column(String(20), nullable=False)
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
