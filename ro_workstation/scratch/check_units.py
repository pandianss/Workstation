
from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import BudgetModel, MISRecordModel
from sqlalchemy import func

def inspect_budgets():
    with get_db_session() as session:
        count = session.query(func.count(BudgetModel.id)).scalar()
        print(f"Total Budget records: {count}")
        
        if count > 0:
            rec = session.query(BudgetModel).first()
            print("\nSample Budget record:")
            for k, v in rec.__dict__.items():
                if not k.startswith('_'):
                    print(f"  {k}: {v}")
                    
        # Check MIS record to see units
        mis_rec = session.query(MISRecordModel).first()
        if mis_rec:
            print("\nSample MIS record (Raw):")
            # Print some key columns
            for k in ['td', 'sb', 'cd', 'gold', 'msme', 'mudra', 'govt_spon']:
                if hasattr(mis_rec, k):
                    print(f"  {k}: {getattr(mis_rec, k)}")

if __name__ == "__main__":
    inspect_budgets()
