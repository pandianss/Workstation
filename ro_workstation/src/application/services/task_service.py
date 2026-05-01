from __future__ import annotations

from datetime import date

import pandas as pd

from src.domain.models.enums import TaskPriority
from src.domain.schemas.task import TaskCreate, TaskRead
from src.infrastructure.llm.client import LLMClient
from src.infrastructure.persistence.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository | None = None) -> None:
        self.repository = repository or TaskRepository()

    def create_task(self, payload: TaskCreate) -> TaskRead:
        return self.repository.create(payload)

    def get_tasks_for_user(self, username: str, limit: int = 50) -> list[TaskRead]:
        return self.repository.list_for_user(username, limit=limit)

    def update_task_status(self, task_id: str, status: str) -> bool:
        return self.repository.update_status(task_id, status)

    def get_task_summary(self, username: str) -> dict:
        tasks = self.get_tasks_for_user(username)
        open_tasks = [task for task in tasks if task.status == "OPEN"]
        overdue = [task for task in open_tasks if task.due_date and task.due_date < date.today()]
        return {
            "open": len(open_tasks),
            "overdue": len(overdue),
            "tasks": [task.model_dump() for task in tasks],
        }

    def parse_nlp_task(self, nl_input: str, username: str, dept: str) -> TaskRead:
        llm = LLMClient()
        prompt = (
            f"Parse this task: '{nl_input}'. "
            "Output JSON with keys: title, priority(P1/P2/P3/P4), due_date(YYYY-MM-DD or null). "
            "Assume due date is today if not specified."
        )
        result = llm.generate_json(prompt, "You are a task parser.")
        priority = str(result.get("priority", "P3")).upper()
        if priority not in {item.value for item in TaskPriority}:
            priority = TaskPriority.P3.value
        try:
            due_date = date.fromisoformat(str(result.get("due_date")))
        except Exception:
            due_date = date.today()
        return self.create_task(
            TaskCreate(
                title=(result.get("title") or nl_input).strip(),
                dept=dept,
                assigned_to=username,
                priority=TaskPriority(priority),
                due_date=due_date,
            )
        )

    def as_frame(self, username: str) -> pd.DataFrame:
        return pd.DataFrame(task.model_dump() for task in self.get_tasks_for_user(username))
