from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
	QDockWidget,
	QFileDialog,
	QHBoxLayout,
	QInputDialog,
	QLabel,
	QMenu,
	QMessageBox,
	QPushButton,
	QTreeWidget,
	QTreeWidgetItem,
	QVBoxLayout,
	QWidget,
)

from app.core.assets import import_images, is_image_file
from app.core.project import Project


class AssetsDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Assets", parent)
		self.setObjectName("AssetsDock")
		self._project: Project | None = None

		container = QWidget(self)
		vbox = QVBoxLayout(container)

		btn_row = QHBoxLayout()
		self._import_btn = QPushButton("Create Tilemap…", container)
		self._import_btn.clicked.connect(self._on_create_tilemap)
		btn_row.addWidget(self._import_btn)
		btn_row.addStretch(1)
		vbox.addLayout(btn_row)

		self._tree = QTreeWidget(container)
		self._tree.setHeaderLabels(["Name"])
		self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
		self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self._tree.customContextMenuRequested.connect(self._on_context_menu)
		self._tree.setAcceptDrops(True)
		self._tree.viewport().setAcceptDrops(True)
		self._tree.installEventFilter(self)
		self._tree.setDragDropMode(QTreeWidget.DragDropMode.DropOnly)
		self.setAcceptDrops(True)
		vbox.addWidget(self._tree)

		self._preview = QLabel(container)
		self._preview.setText("No preview")
		self._preview.setMinimumHeight(120)
		self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self._preview.setStyleSheet("border: 1px solid #555; background: #222; color: #aaa;")
		vbox.addWidget(self._preview)

		container.setLayout(vbox)
		self.setWidget(container)

	def set_project(self, project: Project | None) -> None:
		self._project = project
		self._rebuild()

	def _rebuild(self) -> None:
		self._tree.clear()
		if not self._project:
			return
		root_item = QTreeWidgetItem([str(self._project.assets_dir.name) + "/"])
		self._tree.addTopLevelItem(root_item)
		if self._project.assets_dir.exists():
			for p in sorted(self._project.assets_dir.iterdir()):
				if p.is_file():
					label = p.name
					if is_image_file(p):
						label += " (img)"
					item = QTreeWidgetItem([label])
					item.setData(0, 0, str(p))
					root_item.addChild(item)
		self._tree.expandAll()
		self._tree.itemSelectionChanged.connect(self._update_preview)
		self._update_preview()

	def eventFilter(self, obj, event):  # noqa: D401
		if obj is self._tree:
			if event.type() in (QEvent.Type.DragEnter, QEvent.Type.DragMove):
				if event.mimeData().hasUrls():
					urls: list[QUrl] = event.mimeData().urls()
					for url in urls:
						p = url.toLocalFile()
						if p:
							from pathlib import Path

							if is_image_file(Path(p)):
								event.acceptProposedAction()
								return True
				return False
			if event.type() == QEvent.Type.Drop:
				if not event.mimeData().hasUrls():
					return False
				paths = []
				for url in event.mimeData().urls():
					p = url.toLocalFile()
					if not p:
						continue
					from pathlib import Path

					pp = Path(p)
					if pp.exists() and is_image_file(pp):
						paths.append(pp)
				if paths:
					if self._project:
						import_images(self._project, paths)
					self._rebuild()
					event.acceptProposedAction()
					return True
				return False
		return super().eventFilter(obj, event)

	def _on_create_tilemap(self) -> None:
		if not self._project:
			QMessageBox.information(
				self,
				"No Project",
				"Open or create a project (File → New/Open)",
			)
			return
		file, _ = QFileDialog.getOpenFileName(
			self,
			"Choose image for Tilemap",
			str(self._project.assets_dir),
			"Images (*.png *.jpg *.jpeg)",
		)
		if not file:
			return
		# Ensure image is inside assets; if not, import it first
		from pathlib import Path

		from app.core.assets import import_images, is_image_file
		p = Path(file)
		if p.parent != self._project.assets_dir:
			if not is_image_file(p):
				QMessageBox.information(self, "Invalid file", "Please choose an image file")
				return
			import_images(self._project, [p])
			p = self._project.assets_dir / p.name
		from app.ui.editors.tilemap_painter import TilemapPainterDialog
		dlg = TilemapPainterDialog(self._project, str(p), self)
		if dlg.exec() == dlg.DialogCode.Accepted:  # type: ignore[attr-defined]
			# on save, the dialog already persists tilemap and injects node
			self._rebuild()

	def _update_preview(self) -> None:
		if not self._project:
			self._preview.setText("No project")
			self._preview.setPixmap(QPixmap())
			return
		items = self._tree.selectedItems()
		if not items:
			self._preview.setText("No preview")
			self._preview.setPixmap(QPixmap())
			return
		item = items[0]
		path_str = item.data(0, 0)
		if not path_str:
			self._preview.setText("No preview")
			self._preview.setPixmap(QPixmap())
			return
		from pathlib import Path

		p = Path(path_str)
		if not p.exists() or not is_image_file(p):
			self._preview.setText(p.name)
			self._preview.setPixmap(QPixmap())
			return
		thumb = p.parent / ".thumbnails" / f"{p.stem}_thumb.png"
		pix = QPixmap(str(thumb if thumb.exists() else p))
		if pix.isNull():
			self._preview.setText(p.name)
			self._preview.setPixmap(QPixmap())
			return
		scaled = pix.scaled(
			160,
			160,
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation,
		)
		self._preview.setPixmap(scaled)
		self._preview.setText("")

	def _on_item_double_clicked(self, item: QTreeWidgetItem) -> None:
		# If image, emit create sprite signal via main window
		path_str = item.data(0, 0)
		if not path_str:
			return
		from pathlib import Path

		p = Path(path_str)
		if not is_image_file(p):
			return
		# Offer region selection
		from app.ui.editors.spritesheet_editor import SpritesheetEditor
		dlg = SpritesheetEditor(str(p), self)
		if dlg.exec() == dlg.DialogCode.Accepted:  # type: ignore[attr-defined]
			region = dlg.get_region()
			mw = self.window()  # type: ignore[assignment]
			try:
				mw.create_sprite_from_asset(str(p), region)  # type: ignore[attr-defined]
			except Exception:
				mw.create_sprite_from_asset(str(p))  # type: ignore[attr-defined]

	def _on_context_menu(self, pos) -> None:
		items = self._tree.selectedItems()
		if not items:
			return
		path_str = items[0].data(0, 0)
		if not path_str:
			return
		from pathlib import Path

		p = Path(path_str)
		menu = QMenu(self)
		if is_image_file(p):
			act_anim = menu.addAction("Open Animation Editor…")
			act_tileset = menu.addAction("Create Tileset…")
			act = menu.exec(self._tree.viewport().mapToGlobal(pos))
			if act is act_anim:
				from app.ui.editors.animation_editor import AnimationEditor

				dlg = AnimationEditor(str(p), parent=self)
				dlg.exec()
			elif act is act_tileset:
				self._create_tileset_for_image(p)


	def _create_tileset_for_image(self, image_path) -> None:
		if not self._project:
			return
		w, ok = QInputDialog.getInt(self, "Tile Width", "Width", 32, 1, 4096, 1)
		if not ok:
			return
		h, ok = QInputDialog.getInt(self, "Tile Height", "Height", 32, 1, 4096, 1)
		if not ok:
			return
		from app.core.tilemap import create_tileset_metadata

		create_tileset_metadata(self._project.assets_dir, image_path, w, h)
		self._rebuild()


