from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel, AdvancesRecordModel
from sqlalchemy import func

def inspect_data():
    with get_db_session() as session:
        # Check MIS records
        mis_count = session.query(func.count(MISRecordModel.id)).scalar()
        print(f"Total MIS records: {mis_count}")
        
        if mis_count > 0:
            rec = session.query(MISRecordModel).first()
            print("\nSample MIS record:")
            for k, v in rec.__dict__.items():
                if not k.startswith('_'):
                    print(f"  {k}: {v}")
        
        # Check Advances records
        adv_count = session.query(func.count(AdvancesRecordModel.id)).scalar()
        print(f"\nTotal Advances records: {adv_count}")
        
        if adv_count > 0:
            rec = session.query(AdvancesRecordModel).first()
            print("\nSample Advances record:")
            for k, v in rec.__dict__.items():
                if not k.startswith('_'):
                    print(f"  {k}: {v}")

if __name__ == "__main__":
    inspect_data()
