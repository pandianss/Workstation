
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(os.getcwd())))

from src.application.services.performance_letter_service import PerformanceLetterService
import datetime
import streamlit as st

def test_actual_generation():
    # Mock streamlit session state
    if not hasattr(st, "session_state"):
        class MockSessionState(dict):
            pass
        st.session_state = MockSessionState()
        st.session_state["mis_needs_ingest"] = False

    service = PerformanceLetterService()
    # Use April 2026 as in the user's screenshot
    target_date = datetime.date(2026, 4, 30)
    
    print(f"Analyzing performance for {target_date}...")
    performance_data = service.get_branch_performance(target_date)
    print(f"Found performance data for {len(performance_data)} branches.")
    
    if not performance_data:
        print("No performance data found. Check if MIS data for this date exists.")
        return

    # Filter for SOL 1013 to see what's being generated for them
    sol_1013 = next((p for p in performance_data if p["sol"] == 1013), None)
    if sol_1013:
        print(f"SOL 1013 Achievements: {[a['parameter'] for a in sol_1013['achievements']]}")
        print(f"SOL 1013 Declines: {[d['parameter'] for d in sol_1013['declines']]}")
    
    try:
        print("Attempting to generate letters zip...")
        zip_data = service.generate_letters_zip(performance_data)
        print(f"Success! Zip size: {len(zip_data)} bytes")
        
        with open("actual_performance_letters.zip", "wb") as f:
            f.write(zip_data)
        print("Saved to actual_performance_letters.zip")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_actual_generation()
