from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QDockWidget,
	QFileDialog,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QListWidget,
	QListWidgetItem,
	QPushButton,
	QSpinBox,
	QVBoxLayout,
	QWidget,
)

from app.core.project import Project
from app.core.tilemap import create_tileset_metadata, list_tilesets


class TilesetsDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Tilesets", parent)
		self.setObjectName("TilesetsDock")
		self._project: Project | None = None

		container = QWidget(self)
		root = QVBoxLayout(container)

		row = QHBoxLayout()
		root.addLayout(row)

		self._list = QListWidget(container)
		self._list.itemDoubleClicked.connect(self._on_open_editor)
		row.addWidget(self._list, 2)

		form = QGridLayout()
		row.addLayout(form, 3)
		form.addWidget(QLabel("Tile Width:"), 0, 0)
		self._tw = QSpinBox(container)
		self._tw.setRange(1, 4096)
		self._tw.setValue(32)
		form.addWidget(self._tw, 0, 1)
		form.addWidget(QLabel("Tile Height:"), 1, 0)
		self._th = QSpinBox(container)
		self._th.setRange(1, 4096)
		self._th.setValue(32)
		form.addWidget(self._th, 1, 1)
		self._choose_btn = QPushButton("Choose Image…", container)
		self._choose_btn.clicked.connect(self._on_choose)
		form.addWidget(self._choose_btn, 2, 0, 1, 2)
		self._import_btn = QPushButton("Import", container)
		self._import_btn.clicked.connect(self._on_import)
		form.addWidget(self._import_btn, 3, 0, 1, 2)
		self._chosen_path: Path | None = None

		container.setLayout(root)
		self.setWidget(container)

	def set_project(self, project: Project | None) -> None:
		self._project = project
		self._reload_list()

	def _reload_list(self) -> None:
		self._list.clear()
		if not self._project:
			return
		for p in list_tilesets(self._project.assets_dir):
			item = QListWidgetItem(p.name, self._list)
			item.setData(Qt.ItemDataRole.UserRole, str(p))

	def _on_choose(self) -> None:
		if not self._project:
			return
		file, _ = QFileDialog.getOpenFileName(
			self,
			"Choose image",
			str(self._project.assets_dir),
			"Images (*.png *.jpg *.jpeg)",
		)
		if file:
			self._chosen_path = Path(file)
			self._choose_btn.setText(self._chosen_path.name)

	def _on_import(self) -> None:
		if not self._project or not self._chosen_path:
			return
		create_tileset_metadata(
			self._project.assets_dir,
			self._chosen_path,
			int(self._tw.value()),
			int(self._th.value()),
		)
		self._chosen_path = None
		self._choose_btn.setText("Choose Image…")
		self._reload_list()

	def _on_open_editor(self, item: QListWidgetItem) -> None:
		from app.ui.editors.tileset_editor import TilesetEditor

		path_str = item.data(Qt.ItemDataRole.UserRole)
		if not path_str:
			return
		TilesetEditor(Path(path_str), self).exec()


