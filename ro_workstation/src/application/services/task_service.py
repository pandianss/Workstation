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
        from datetime import date as _date
        llm = LLMClient()
        today = _date.today().isoformat()
        prompt = (
            f"Parse the following task instruction and extract structured data.\n\n"
            f"TASK INSTRUCTION: \"{nl_input}\"\n\n"
            "Return ONLY a valid JSON object with exactly these keys — "
            "no markdown fences, no explanation before or after the JSON:\n"
            "{{\n"
            "  \"title\": \"<short imperative task title, max 12 words>\",\n"
            "  \"priority\": \"<one of: P1, P2, P3, P4>\",\n"
            "  \"due_date\": \"<YYYY-MM-DD if a specific date is mentioned, else null>\",\n"
            "  \"tags\": [\"<keyword1>\", \"<keyword2>\"]\n"
            "}}\n\n"
            "PRIORITY GUIDE:\n"
            "- P1: urgent, immediate, ASAP, critical, today, emergency\n"
            "- P2: high priority, important, this week, overdue, soon\n"
            "- P3: default — use when no priority signal is present\n"
            "- P4: low priority, whenever, no rush, eventually\n\n"
            f"Today's date: {today}\n"
            "If a relative date is given (e.g., 'by Friday', 'next week'), "
            f"compute the absolute date from today ({today})."
        )
        try:
            result = llm.generate_json(prompt, "You are a precise task extraction engine.")
        except (RuntimeError, ValueError):
            result = {}

        priority = str(result.get("priority", "P3")).upper()
        if priority not in {item.value for item in TaskPriority}:
            priority = TaskPriority.P3.value
        try:
            due_date = date.fromisoformat(str(result.get("due_date") or ""))
        except (ValueError, TypeError):
            due_date = date.today()
        title = (result.get("title") or nl_input).strip()[:200]

        return self.create_task(
            TaskCreate(
                title=title,
                dept=dept,
                assigned_to=username,
                priority=TaskPriority(priority),
                due_date=due_date,
            )
        )

    def as_frame(self, username: str) -> pd.DataFrame:
        return pd.DataFrame(task.model_dump() for task in self.get_tasks_for_user(username))
