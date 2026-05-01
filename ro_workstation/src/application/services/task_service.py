from __future__ import annotations

from datetime import date

import pandas as pd

from src.domain.models.enums import TaskPriority
from src.domain.schemas.task import TaskCreate, TaskRead
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


    def as_frame(self, username: str) -> pd.DataFrame:
        return pd.DataFrame(task.model_dump() for task in self.get_tasks_for_user(username))
