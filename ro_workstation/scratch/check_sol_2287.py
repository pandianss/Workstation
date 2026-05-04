
from src.application.services.performance_letter_service import PerformanceLetterService
import datetime
import streamlit as st

def check_1013():
    if not hasattr(st, "session_state"):
        class MockSessionState(dict): pass
        st.session_state = MockSessionState()
        st.session_state["mis_needs_ingest"] = False
    
    service = PerformanceLetterService()
    target_date = datetime.date(2026, 4, 30)
    data = service.get_branch_performance(target_date)
    
    sol_1013 = next((p for p in data if p["sol"] == 1013), None)
    if sol_1013:
        print(f"SOL 1013:")
        print(f"  Achievements: {len(sol_1013['achievements'])}")
        for a in sol_1013['achievements']:
            print(f"    - {a['parameter']}: Actual {a['actual']}, Target {a['target']}, Pct {a['pct']:.1f}%")
        print(f"  Declines: {len(sol_1013['declines'])}")
        for d in sol_1013['declines']:
            print(f"    - {d['parameter']}: Actual {d['actual']}, Target {d['target']}, Pct {d['pct']:.1f}%")
    else:
        print("SOL 1013 not found in performance data.")

if __name__ == "__main__":
    check_1013()
