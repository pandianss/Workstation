from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MasterRecordModel, MISRecordModel
from sqlalchemy import func

def check_sol():
    with get_db_session() as session:
        # Check SOL 3933
        rec = session.query(MasterRecordModel).filter(MasterRecordModel.code == '3933').first()
        if rec:
            print(f"SOL 3933: {rec.name_en} ({rec.category})")
        else:
            print("SOL 3933 not found in masters.")
            
        # Check distinct SOLs in MIS records
        sols = session.query(MISRecordModel.sol).distinct().all()
        print(f"Distinct SOLs in MIS: {len(sols)}")
        print(f"SOL list (sample): {[s[0] for s in sols[:10]]}")

if __name__ == "__main__":
    check_sol()
