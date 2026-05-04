
import os
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(os.getcwd())))

from src.core.paths import project_path

def re_ingest():
    mis_dir = project_path("data", "mis")
    archive_dir = mis_dir / "archive"
    db_path = project_path("data", "mis_store.db")
    budget_sync_path = project_path("data", "budget_sync.json")
    
    print(f"Checking for files in {archive_dir}...")
    if archive_dir.exists():
        files = list(archive_dir.glob("*.xlsx"))
        print(f"Found {len(files)} files to move back.")
        for f in files:
            print(f"Moving {f.name} back to {mis_dir}")
            shutil.move(str(f), str(mis_dir / f.name))
            
    if db_path.exists():
        print(f"Deleting existing database at {db_path}...")
        os.remove(db_path)

    if budget_sync_path.exists():
        print(f"Resetting budget sync state...")
        os.remove(budget_sync_path)
        
    print("Triggering re-ingestion via MISAnalyticsService...")
    from src.application.use_cases.mis.service import MISAnalyticsService
    # We need to mock st.session_state if running outside Streamlit
    import streamlit as st
    if not hasattr(st, "session_state"):
        class MockSessionState(dict):
            pass
        st.session_state = MockSessionState()
        
    service = MISAnalyticsService()
    # Force ingestion
    service.get_data(force_ingest=True)
    print("Re-ingestion complete.")

if __name__ == "__main__":
    re_ingest()
