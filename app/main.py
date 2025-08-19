from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from app.core.settings import EditorSettings, load_settings
from app.ui.main_window import MainWindow


def main() -> None:
	app = QApplication(sys.argv)
	settings: EditorSettings = load_settings()
	window = MainWindow()
	# Применяем тему из настроек
	_apply_theme(app, settings.theme)

	# Попытаться открыть последний проект
	try:
		from app.core.project import open_project

		last = settings.recent_projects[0] if settings.recent_projects else None
		if last:
			p = Path(last)
			project = open_project(p)
			window._set_current_project(project)
	except Exception:
		# Игнорируем ошибки — откроется пустой проект
		pass

	window.showMaximized()
	code = app.exec()
	sys.exit(code)


def _apply_theme(app: QApplication, theme: str) -> None:
	from pathlib import Path

	base = Path(__file__).resolve().parent / "ui" / "themes"
	file = base / ("dark.qss" if theme == "dark" else "light.qss")
	try:
		app.setStyleSheet(file.read_text(encoding="utf-8"))
	except Exception:
		app.setStyleSheet("")


if __name__ == "__main__":
	main()


