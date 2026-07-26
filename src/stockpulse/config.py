"""Configuration — YAML + env vars."""

import os
import yaml
from pathlib import Path
from typing import Optional


CONFIG_PATHS = [
    Path("config.yaml"),
    Path.home() / ".stockpulse" / "config.yaml",
]


class Settings:
    """Settings loaded from YAML then overridden by env vars."""

    def __init__(self):
        self._data = {
            "host": "localhost",
            "port": 8900,
            "log_level": "info",
            "pg_uri": None,
        }
        self._loaded = None
        self._load_file()
        self._apply_env()
        if self._data["pg_uri"] is None:
            self._data["pg_uri"] = self._resolve_pg_uri()

    @staticmethod
    def _resolve_pg_uri() -> str:
        uri = os.environ.get("STOCKPULSE_PG_URI")
        if uri:
            return uri
        user = os.environ.get("USER", "zrall")
        host = os.environ.get("PG_HOST", "localhost")
        db = os.environ.get("PG_DB", "ashare")
        return f"postgresql://{user}@{host}/{db}?options=-c%20search_path=ashare,public"

    def _load_file(self):
        for path in CONFIG_PATHS:
            if path.exists():
                with open(path) as f:
                    cfg = yaml.safe_load(f) or {}
                self._loaded = path
                for k in ("pg_uri", "host", "port", "log_level"):
                    if k in cfg:
                        self._data[k] = cfg[k]
                break

    def _apply_env(self):
        mapping = {
            "pg_uri": "STOCKPULSE_PG_URI",
            "host": "STOCKPULSE_HOST",
            "port": "STOCKPULSE_PORT",
            "log_level": "STOCKPULSE_LOG_LEVEL",
        }
        for key, env_name in mapping.items():
            val = os.environ.get(env_name)
            if val is not None:
                self._data[key] = val

    @property
    def pg_uri(self) -> str:
        return self._data.get("pg_uri") or self._resolve_pg_uri()

    @property
    def host(self) -> str:
        return self._data.get("host", "localhost")

    @property
    def port(self) -> int:
        return int(self._data.get("port", 8900))

    @property
    def log_level(self) -> str:
        return self._data.get("log_level", "info")

    def loaded_from(self) -> Optional[str]:
        return str(self._loaded) if self._loaded else None


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
