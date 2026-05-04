from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel

def check_branch():
    with get_db_session() as session:
        # Check a typical branch
        rec = session.query(MISRecordModel).filter(MISRecordModel.sol != 3933).first()
        if rec:
            print(f"Sample Branch SOL {rec.sol}:")
            for k, v in rec.__dict__.items():
                if not k.startswith('_'):
                    print(f"  {k}: {v}")
        else:
            print("No branch records found.")

if __name__ == "__main__":
    check_branch()
