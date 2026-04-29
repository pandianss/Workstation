import sys
import os
import uuid
import random
from datetime import datetime, date, timedelta

# Ensure we can import from ro_workstation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.tasks.models import Task, Base
from modules.tasks.engine import Session, engine

# Create tables
Base.metadata.create_all(engine)

def seed_tasks():
    session = Session()
    
    # Clear existing mock tasks
    session.query(Task).delete()
    
    tasks_to_create = [
        {"title": "Submit PMJDY Monthly Return", "dept": "FI", "priority": "P2", "task_type": "RETURN_DUE", "due_days": 2},
        {"title": "Review SMA-2 Slippages (Rs 15Cr)", "dept": "CRMD", "priority": "P1", "task_type": "SMA_ALERT", "due_days": 0},
        {"title": "Quarterly Performance Review Prep", "dept": "PLAN", "priority": "P3", "task_type": "MEETING_PREP", "due_days": 5},
        {"title": "KCC Renewal Drive Follow-up", "dept": "ARID", "priority": "P3", "task_type": "CIRCULAR_ACTION", "due_days": 7},
        {"title": "Pending JAIIB Nominations", "dept": "HRDD", "priority": "P4", "task_type": "PERSONAL", "due_days": 10},
        {"title": "Palani Branch Lease Renewal", "dept": "GAD", "priority": "P2", "task_type": "ASSIGNED", "due_days": 3},
        {"title": "Compliance Certificate Submission", "dept": "COM", "priority": "P1", "task_type": "RETURN_DUE", "due_days": -1},
        {"title": "Retail CASA Drive Launch", "dept": "MKT", "priority": "P3", "task_type": "CIRCULAR_ACTION", "due_days": 4},
        {"title": "DRT Hearing - ABC Traders", "dept": "LAW", "priority": "P2", "task_type": "ASSIGNED", "due_days": 2},
        {"title": "Review Batlagundu Audit Report", "dept": "INS", "priority": "P3", "task_type": "ASSIGNED", "due_days": 6},
        {"title": "Risk Dashbaord Approval", "dept": "RSK", "priority": "P2", "task_type": "RETURN_DUE", "due_days": 1},
        {"title": "MUDRA Disbursement Follow-up", "dept": "SME", "priority": "P3", "task_type": "ASSIGNED", "due_days": 5},
        {"title": "Home Loan Campaign Tracker", "dept": "RET", "priority": "P4", "task_type": "RETURN_DUE", "due_days": 12},
        {"title": "CBS Downtime RCA - Athoor", "dept": "RCC", "priority": "P1", "task_type": "ASSIGNED", "due_days": 0},
    ]

    for t in tasks_to_create:
        due_date = date.today() + timedelta(days=t["due_days"])
        status = "OPEN"
        
        # Add tasks to admin for visibility
        task = Task(
            id=str(uuid.uuid4()),
            title=t["title"],
            description=f"Mock task generated for {t['dept']} department.",
            dept=t["dept"],
            task_type=t["task_type"],
            priority=t["priority"],
            due_date=due_date,
            assigned_to="admin",  # Assigning to the default testing user
            status=status,
            source="mock_seeder",
            created_at=datetime.utcnow()
        )
        session.add(task)

    session.commit()
    session.close()
    print(f"Successfully seeded {len(tasks_to_create)} tasks into the database.")

if __name__ == "__main__":
    seed_tasks()
