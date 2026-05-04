from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MasterRecordModel, MISRecordModel
from sqlalchemy import func
import datetime

def find_branch(name):
    with get_db_session() as session:
        b = session.query(MasterRecordModel).filter(MasterRecordModel.name_en.like(f"%{name}%")).first()
        if b:
            print(f"Found {b.name_en} with SOL {b.code}")
            latest_date = session.query(func.max(MISRecordModel.date)).scalar()
            prev_month_end = latest_date.replace(day=1) - datetime.timedelta(days=1)
            prev_date = session.query(func.max(MISRecordModel.date)).filter(MISRecordModel.date <= prev_month_end).scalar()
            
            for date in [latest_date, prev_date]:
                r = session.query(MISRecordModel).filter(MISRecordModel.sol == int(b.code), MISRecordModel.date == date).first()
                if r:
                    sb = r.sb / 100
                    cd = r.cd / 100
                    td = r.td / 100
                    agri = r.core_agri / 100
                    msme = r.msme / 100
                    gold = r.gold / 100
                    core_retail = (r.housing + r.vehicle + r.personal + r.education + r.mortgage + r.liquirent + r.other_retail) / 100
                    biz_with_gold = sb + cd + td + agri + msme + gold + core_retail
                    biz_without_gold = sb + cd + td + agri + msme + core_retail
                    print(f"  Date {date}: Biz(With Gold)={biz_with_gold:.2f}, Biz(No Gold)={biz_without_gold:.2f}")

if __name__ == "__main__":
    find_branch("Medical College")
