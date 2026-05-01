from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from src.core.paths import project_path


class AppSettings(BaseModel):
    environment: str = Field(default="development")
    app_title: str = Field(default="RO Workstation")
    ollama_model: str = Field(default="mistral")
    ollama_host: str = Field(default="http://localhost:11434")
    offline_mode: bool = Field(default=True)
    admin_password: str = Field(default="admin")
    max_tasks_displayed: int = Field(default=100)
    region_code: str = Field(default="3933")
    session_timeout_hours: int = Field(default=4)


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_app_settings() -> AppSettings:
    """Load environment-aware settings from data config and env vars."""
    data = _load_json_file(project_path("data", "config.json"))
    env_path = project_path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            data.setdefault(key.strip().lower(), value.strip())

    normalized = {
        "environment": data.get("environment", data.get("env", "development")),
        "app_title": data.get("app_title", "RO Workstation"),
        "ollama_model": data.get("ollama_model", "mistral"),
        "ollama_host": data.get("ollama_host", "http://localhost:11434"),
        "offline_mode": str(data.get("offline_mode", "true")).lower() == "true",
        "admin_password": data.get("admin_password", "admin"),
        "max_tasks_displayed": int(data.get("max_tasks_displayed", 100)),
        "region_code": str(data.get("region_code", "3933")),
        "session_timeout_hours": int(data.get("session_timeout_hours", 4)),
    }
    return AppSettings.model_validate(normalized)


@lru_cache(maxsize=16)
def load_yaml_config(name: str) -> dict[str, Any]:
    """Load and cache YAML configuration from the config directory."""
    path = project_path("src", "config", name)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping config in {path}")
    return loaded


def load_yaml(path: str) -> dict[str, Any]:
    """Compatibility wrapper for load_yaml_config."""
    name = path.split("/")[-1]
    return load_yaml_config(name)
