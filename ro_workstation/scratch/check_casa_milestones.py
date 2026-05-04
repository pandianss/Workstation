from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel
from sqlalchemy import func

def check_casa():
    with get_db_session() as session:
        latest_date = session.query(func.max(MISRecordModel.date)).scalar()
        recs = session.query(MISRecordModel).filter(MISRecordModel.date == latest_date).all()
        
        casa_50 = []
        for r in recs:
            if r.sol == 3933: continue
            casa = (r.sb + r.cd) / 100
            if casa >= 50:
                casa_50.append((r.sol, casa))
        
        print(f"CASA milestones (>= 50Cr) on {latest_date}: {len(casa_50)}")
        for sol, val in sorted(casa_50, key=lambda x: x[1], reverse=True):
            print(f"  SOL {sol}: {val:.2f} Cr")

if __name__ == "__main__":
    check_casa()
