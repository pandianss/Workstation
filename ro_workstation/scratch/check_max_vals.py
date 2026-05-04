from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel
from sqlalchemy import func
from src.application.services.milestone_service import MilestoneService

def check_max_values():
    with get_db_session() as session:
        latest_date = session.query(func.max(MISRecordModel.date)).scalar()
        recs = session.query(MISRecordModel).filter(MISRecordModel.date == latest_date).all()
        
        ms = MilestoneService(session)
        max_vals = {p: 0.0 for p in ms.PARAMETERS}
        
        for r in recs:
            if r.sol == 3933: continue
            vals = ms._calculate_parameters(r)
            for p, v in vals.items():
                if v > max_vals[p]:
                    max_vals[p] = v
        
        print(f"Max Values across all branches (Cr) on {latest_date}:")
        for p, v in max_vals.items():
            print(f"  {p}: {v:.2f}")

if __name__ == "__main__":
    check_max_values()
