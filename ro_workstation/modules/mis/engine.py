import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, MISRecord, IngestedFile
from ..utils.paths import project_path

DB_PATH = project_path("data", "mis_store.db")

def _initialize_engine():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}")
    Base.metadata.create_all(engine)
    return engine

engine = _initialize_engine()
Session = sessionmaker(bind=engine)

def is_file_ingested(filename):
    session = Session()
    exists = session.query(IngestedFile).filter(IngestedFile.filename == filename).first() is not None
    session.close()
    return exists

def mark_file_ingested(filename):
    session = Session()
    new_file = IngestedFile(filename=filename)
    session.add(new_file)
    session.commit()
    session.close()

def save_mis_records(records_list):
    """Expects a list of dictionaries mapping to MISRecord columns."""
    session = Session()
    try:
        # Convert list of dicts to MISRecord objects
        objs = []
        for r in records_list:
            # Normalize column names to lowercase to match model
            normalized = {k.lower().replace(" ", "_"): v for k, v in r.items()}
            # Remove any keys not in the model
            valid_keys = MISRecord.__table__.columns.keys()
            filtered = {k: v for k, v in normalized.items() if k in valid_keys}
            
            # Special handling for date
            if 'date' in filtered and isinstance(filtered['date'], str):
                 filtered['date'] = pd.to_datetime(filtered['date']).date()
            elif 'date' in filtered and hasattr(filtered['date'], 'date'):
                 filtered['date'] = filtered['date'].date()
            
            objs.append(MISRecord(**filtered))
            
        session.bulk_save_objects(objs)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_mis_data():
    session = Session()
    query = session.query(MISRecord)
    df = pd.read_sql(query.statement, engine)
    session.close()
    
    # Clean up column names for dashboard (uppercase and spaces)
    # The dashboard expects specific names like "Total Advances" which are derived.
    # We will let mis_service handle the derived metrics.
    return df
