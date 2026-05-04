from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel
from sqlalchemy import func
import datetime

def check_history():
    with get_db_session() as session:
        latest_date = session.query(func.max(MISRecordModel.date)).scalar()
        prev_month_end = latest_date.replace(day=1) - datetime.timedelta(days=1)
        prev_date = session.query(func.max(MISRecordModel.date)).filter(MISRecordModel.date <= prev_month_end).scalar()
        
        print(f"Comparing {latest_date} with {prev_date}")
        
        for date in [latest_date, prev_date]:
            rec = session.query(MISRecordModel).filter(MISRecordModel.sol == 2287, MISRecordModel.date == date).first()
            if rec:
                # Business calc
                sb = rec.sb / 100
                cd = rec.cd / 100
                td = rec.td / 100
                agri = rec.core_agri / 100
                msme = rec.msme / 100
                gold = rec.gold / 100
                core_retail = (rec.housing + rec.vehicle + rec.personal + rec.education + rec.mortgage + rec.liquirent + rec.other_retail) / 100
                biz = sb + cd + td + agri + msme + gold + core_retail
                print(f"  Date {date}: Business = {biz:.2f} Cr")
            else:
                print(f"  No record for {date}")

if __name__ == "__main__":
    check_history()
