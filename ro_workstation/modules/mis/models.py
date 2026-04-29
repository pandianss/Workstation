from sqlalchemy import Column, Integer, Float, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MISRecord(Base):
    __tablename__ = 'mis_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    sol = Column(Integer, nullable=False, index=True)
    
    # Financial Metrics (Floats)
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
    
    kcc = Column(Float, default=0.0)
    shg = Column(Float, default=0.0)
    govt_spon = Column(Float, default=0.0)
    oth_schematic = Column(Float, default=0.0)
    retail_jl = Column(Float, default=0.0)
    agri_jl = Column(Float, default=0.0)
    mudra = Column(Float, default=0.0)

class IngestedFile(Base):
    __tablename__ = 'ingested_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    ingested_at = Column(DateTime, default=datetime.now)
