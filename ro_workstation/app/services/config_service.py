import json
from pathlib import Path

DATA_DIR = Path("app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = DATA_DIR / "config.json"

# Initialize if doesn't exist
if not CONFIG_FILE.exists():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"theme": "light", "max_tasks_displayed": 100}, f)

def get_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def get_value(key, default=None):
    config = get_config()
    return config.get(key, default)
