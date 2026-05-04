from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel
from sqlalchemy import func

def check_dates():
    with get_db_session() as session:
        dates = session.query(MISRecordModel.date).distinct().order_by(MISRecordModel.date.desc()).all()
        date_list = [d[0] for d in dates]
        print(f"Dates available: {date_list}")
        
        if len(date_list) >= 2:
            latest = date_list[0]
            previous = date_list[1]
            print(f"Latest: {latest}, Previous: {previous}")

if __name__ == "__main__":
    check_dates()
