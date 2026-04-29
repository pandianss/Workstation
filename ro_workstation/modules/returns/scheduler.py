import yaml
from ..utils.paths import project_path


def load_department_config():
    try:
        with project_path("config", "dept_config.yaml").open(encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except Exception:
        return {}

def get_upcoming_returns(dept: str):
    dept_config = load_department_config()
    return dept_config.get(dept, {}).get("returns", [])
