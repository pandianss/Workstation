from datetime import date
from pathlib import Path
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from .models import Base, Task, Reminder
from ..utils.paths import project_path

VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}
DEFAULT_DB_PATH = project_path("data", "ro_tasks.db")
FALLBACK_DB_PATH = Path(tempfile.gettempdir()) / "ro_workstation" / "ro_tasks.db"


def _initialize_engine():
    for candidate in (DEFAULT_DB_PATH, FALLBACK_DB_PATH):
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate_engine = create_engine(f"sqlite:///{candidate.as_posix()}")
            Base.metadata.create_all(candidate_engine)
            return candidate_engine, candidate
        except OperationalError:
            continue

    memory_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(memory_engine)
    return memory_engine, Path(":memory:")


engine, ACTIVE_DB_PATH = _initialize_engine()
Session = sessionmaker(bind=engine)

def create_task(title, dept, assigned_to, priority="P3", due_date=None, task_type="PERSONAL", source="user", description=""):
    session = Session()
    new_task = Task(
        title=title,
        description=description,
        dept=dept,
        task_type=task_type,
        priority=priority,
        due_date=due_date,
        assigned_to=assigned_to,
        source=source
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    session.close()
    return new_task

def get_tasks_for_user(username, limit=50):
    session = Session()
    tasks = session.query(Task).filter(Task.assigned_to == username).all()
    session.close()
    return sorted(tasks, key=_task_sort_key)[:limit]

def update_task_status(task_id, status):
    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        session.commit()
        session.close()
        return True
    session.close()
    return False


def _normalize_priority(value):
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in VALID_PRIORITIES:
            return normalized
    return "P3"


def _task_sort_key(task):
    return (
        0 if getattr(task, "status", None) == "OPEN" else 1,
        1 if getattr(task, "due_date", None) is None else 0,
        getattr(task, "due_date", None) or date.max,
        -(getattr(task, "created_at", None) or date.min).toordinal()
        if hasattr((getattr(task, "created_at", None) or date.min), "toordinal")
        else 0,
    )


def _parse_due_date(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return date.today()
    return date.today()

def parse_nlp_task(nl_input: str, username: str, dept: str):
    """Create a task from natural language with safe fallbacks."""
    from ..llm.client import LLMClient
    llm = LLMClient()
    prompt = (
        f"Parse this task: '{nl_input}'. "
        "Output JSON with keys: title, priority(P1/P2/P3/P4), due_date(YYYY-MM-DD or null). "
        "Assume due date is today if not specified."
    )
    res = llm.generate_json(prompt, "You are a task parser.")
    title = res.get("title") if isinstance(res.get("title"), str) and res.get("title").strip() else nl_input
    priority = _normalize_priority(res.get("priority"))
    due_date = _parse_due_date(res.get("due_date"))
    return create_task(title=title.strip(), dept=dept, assigned_to=username, priority=priority, due_date=due_date)
