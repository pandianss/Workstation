from .engine import create_task, Session
from .models import Task
from datetime import date, timedelta
from ..returns.scheduler import load_department_config

def generate_return_tasks():
    """
    Reads config/dept_config.yaml and generates tasks for returns due.
    """
    dept_config = load_department_config()
    
    session = Session()
    today = date.today()
    
    for dept, data in dept_config.items():
        returns = data.get('returns', [])
        for ret in returns:
            # Dummy logic: just create a task for demonstration if not exists
            # In a real app we'd calculate due_date from due_day/due_month_day
            title = f"Submit: {ret['name']}"
            existing = session.query(Task).filter_by(title=title, dept=dept, status="OPEN").first()
            if not existing:
                create_task(
                    title=title,
                    description=f"Format: {ret.get('format', 'N/A')}, Recipient: {ret.get('recipient', 'N/A')}",
                    dept=dept,
                    assigned_to=f"{dept.lower()}_head",  # e.g. fi_head
                    priority="P2",
                    due_date=today + timedelta(days=3),
                    task_type="RETURN_DUE",
                    source="returns_scheduler"
                )
    session.close()
