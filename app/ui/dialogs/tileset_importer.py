from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QListWidget,
	QListWidgetItem,
	QPushButton,
	QSpinBox,
	QVBoxLayout,
)

from app.core.project import Project
from app.core.tilemap import create_tileset_metadata, list_tilesets


class TilesetImportDialog(QDialog):
	def __init__(self, project: Project, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Tilesets")
		self._project = project

		main = QVBoxLayout(self)
		row = QHBoxLayout()
		main.addLayout(row)

		# Left: list of tilesets
		self._list = QListWidget(self)
		row.addWidget(self._list, 2)

		# Right: controls to import new tileset
		right = QGridLayout()
		row.addLayout(right, 3)
		right.addWidget(QLabel("Tile Width:"), 0, 0)
		self._tw = QSpinBox(self)
		self._tw.setRange(1, 4096)
		self._tw.setValue(32)
		right.addWidget(self._tw, 0, 1)
		right.addWidget(QLabel("Tile Height:"), 1, 0)
		self._th = QSpinBox(self)
		self._th.setRange(1, 4096)
		self._th.setValue(32)
		right.addWidget(self._th, 1, 1)
		self._choose_btn = QPushButton("Choose Image…", self)
		self._choose_btn.clicked.connect(self._on_choose)
		right.addWidget(self._choose_btn, 2, 0, 1, 2)
		self._import_btn = QPushButton("Import", self)
		self._import_btn.clicked.connect(self._on_import)
		right.addWidget(self._import_btn, 3, 0, 1, 2)
		self._chosen_path: Path | None = None

		# Bottom buttons
		btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
		btns.rejected.connect(self.reject)
		btns.accepted.connect(self.accept)
		main.addWidget(btns)

		self._reload_list()

	def _reload_list(self) -> None:
		self._list.clear()
		for p in list_tilesets(self._project.assets_dir):
			QListWidgetItem(p.name, self._list).setData(Qt.ItemDataRole.UserRole, str(p))

	def _on_choose(self) -> None:
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
		if not self._chosen_path:
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


