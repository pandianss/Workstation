
from src.infrastructure.persistence.budget_repository import BudgetRepository
import datetime

def debug_target():
    repo = BudgetRepository()
    # Test for SOL 1013, Total Deposits, April 2026
    metric = "Total Deposits"
    year_month = "2026-04"
    sols = [1013]
    
    excel_param = repo.param_map.get(metric.upper(), repo.param_map.get(metric, metric))
    print(f"Metric: {metric} -> Excel Param: {excel_param}")
    
    target = repo.get_target(metric, year_month, sols)
    print(f"Retrieved target: {target}")
    
    # Check what's in the DB manually
    from src.infrastructure.persistence.database import get_db_session
    from src.infrastructure.persistence.sqlite_models import BudgetModel
    from sqlalchemy import func
    
    with get_db_session() as session:
        # Check raw records for this param
        count = session.query(BudgetModel).filter(BudgetModel.parameter == excel_param).count()
        print(f"Total records in DB for {excel_param}: {count}")
        
        # Check for specific SOL and Date
        target_dt = datetime.date(2026, 4, 30)
        rec = session.query(BudgetModel).filter(
            BudgetModel.parameter == excel_param,
            BudgetModel.sol == 1013
        ).all()
        print(f"Records for SOL 1013 and {excel_param}: {len(rec)}")
        for r in rec:
            print(f"  {r.date} -> {r.target} (type(date): {type(r.date)})")

if __name__ == "__main__":
    debug_target()
