
from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import BudgetModel
from sqlalchemy import func
import sys
from pathlib import Path
import os

def check_sol_budgets(sol):
    with get_db_session() as session:
        # Check all budgets for this SOL
        budgets = session.query(BudgetModel).filter(BudgetModel.sol == sol).all()
        print(f"Budgets for SOL {sol}: {len(budgets)}")
        for b in budgets:
            print(f"  {b.parameter}: {b.target} on {b.date}")

if __name__ == "__main__":
    check_sol_budgets(1013)
