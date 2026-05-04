
from src.application.services.performance_letter_service import PerformanceLetterService
import datetime
import streamlit as st

def debug_casa_1013():
    if not hasattr(st, "session_state"):
        class MockSessionState(dict): pass
        st.session_state = MockSessionState()
        st.session_state["mis_needs_ingest"] = False
    
    service = PerformanceLetterService()
    target_date = datetime.date(2026, 4, 30)
    df = service.analytics_service.get_data()
    row = df[(df["SOL"] == 1013) & (df["DATE"].dt.date == target_date)].iloc[0]
    
    p = "CASA"
    actual = row.get(p.upper(), row.get(p, 0.0))
    target = service.budget_repo.get_target(p, target_date.strftime("%Y-%m"), sols=[1013])
    
    print(f"CASA Debug for SOL 1013:")
    print(f"  Actual: {actual}")
    print(f"  Target: {target}")
    if target > 0:
        pct = actual / target * 100
        print(f"  Pct: {pct}%")

if __name__ == "__main__":
    debug_casa_1013()
