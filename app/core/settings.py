from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel


def get_config_dir() -> Path:
	if os.name == "nt":
		root = os.getenv("APPDATA")
		if not root:
			root = str(Path.home() / "AppData" / "Roaming")
		return Path(root) / "dedART"
	# POSIX
	xdg = os.getenv("XDG_CONFIG_HOME")
	root = Path(xdg) if xdg else (Path.home() / ".config")
	return root / "dedART"


CONFIG_FILE: Path = get_config_dir() / "settings.json"



class EditorSettings(BaseModel):
	version: int = 1
	theme: str = "dark"
	recent_projects: list[str] = []
	autosave_minutes: int = 10
	grid_enabled: bool = True
	grid_step: int = 32
	snap_to_grid: bool = True


def load_settings() -> EditorSettings:
	config_dir = get_config_dir()
	config_dir.mkdir(parents=True, exist_ok=True)
	if CONFIG_FILE.exists():
		try:
			data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
			# Миграция: если старая версия (или отсутствует), переключить дефолт на dark
			if not isinstance(data, dict):
				return EditorSettings()
			version = int(data.get("version", 0))
			if version < 1:
				data["version"] = 1
				# Принудительно выставляем тёмную тему при миграции с ранних версий
				data["theme"] = "dark"
				settings = EditorSettings(**data)
				save_settings(settings)
				return settings
			# Миграция до v2: единоразово принудительно перевести тему в dark,
			# чтобы исправить ранние установки по умолчанию (light)
			if version < 2:
				data["version"] = 2
				data["theme"] = "dark"
				settings = EditorSettings(**data)
				save_settings(settings)
				return settings
			# Миграция до v3: гарантированно установить dark как стартовый дефолт
			if version < 3:
				data["version"] = 3
				data["theme"] = "dark"
				settings = EditorSettings(**data)
				save_settings(settings)
				return settings
			# v4: добавить настройки сетки по умолчанию
			if version < 4:
				data["version"] = 4
				data.setdefault("grid_enabled", True)
				data.setdefault("grid_step", 32)
				settings = EditorSettings(**data)
				save_settings(settings)
				return settings
			# v5: добавить привязку к сетке по умолчанию
			if version < 5:
				data["version"] = 5
				data.setdefault("snap_to_grid", True)
				settings = EditorSettings(**data)
				save_settings(settings)
				return settings
			return EditorSettings(**data)
		except Exception:
			return EditorSettings()
	settings = EditorSettings()
	CONFIG_FILE.write_text(settings.model_dump_json(indent=2), encoding="utf-8")
	return settings


def save_settings(settings: EditorSettings) -> None:
	config_dir = get_config_dir()
	config_dir.mkdir(parents=True, exist_ok=True)
	CONFIG_FILE.write_text(settings.model_dump_json(indent=2), encoding="utf-8")


def add_recent_project(path: str) -> None:
	settings = load_settings()
	# Переместить путь в начало списка, убрать дубликаты, ограничить 5
	paths = [p for p in settings.recent_projects if p != path]
	paths.insert(0, path)
	settings.recent_projects = paths[:5]
	save_settings(settings)


