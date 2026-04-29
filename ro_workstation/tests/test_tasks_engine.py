import unittest
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from modules.tasks import engine


class TaskEngineTests(unittest.TestCase):
    def test_get_tasks_for_user_prioritizes_open_and_earlier_due_dates(self):
        now = datetime.now()
        done = SimpleNamespace(id="3", status="DONE", due_date=date.today() - timedelta(days=5), created_at=now)
        open_later = SimpleNamespace(id="2", status="OPEN", due_date=date.today() + timedelta(days=3), created_at=now)
        open_earlier = SimpleNamespace(id="1", status="OPEN", due_date=date.today() + timedelta(days=1), created_at=now)

        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def all(self):
                return [done, open_later, open_earlier]

        class FakeSession:
            def query(self, *args, **kwargs):
                return FakeQuery()

            def close(self):
                return None

        with patch("modules.tasks.engine.Session", return_value=FakeSession()):
            tasks = engine.get_tasks_for_user("test_user", limit=10)

        ordered_ids = [task.id for task in tasks[:3]]
        self.assertEqual(ordered_ids, [open_earlier.id, open_later.id, done.id])

    def test_parse_nlp_task_normalizes_invalid_priority_and_due_date(self):
        with patch("modules.llm.client.LLMClient.generate_json", return_value={
                "title": "Follow up with branch",
                "priority": "urgent",
                "due_date": "not-a-date",
            }):
            with patch("modules.tasks.engine.create_task") as mock_create_task:
                engine.parse_nlp_task("follow up", "test_user", "CRMD")

        mock_create_task.assert_called_once_with(
            title="Follow up with branch",
            dept="CRMD",
            assigned_to="test_user",
            priority="P3",
            due_date=date.today(),
        )


if __name__ == "__main__":
    unittest.main()
