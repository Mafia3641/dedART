from __future__ import annotations

from pathlib import Path
from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.project import Project
from app.core.scene import TilemapNode
from app.core.tilemap import TileLayer, Tilemap, Tileset, create_tileset_metadata

Tool = Literal["pencil", "rect", "fill"]


class TilemapPainterDialog(QDialog):
	def __init__(self, project: Project, image_path: str, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Tilemap Editor")
		self._project = project
		self._image_path = Path(image_path)
		self._tileset_path = create_tileset_metadata(project.assets_dir, Path(image_path), 32, 32)
		self._tileset = Tileset.load_json(self._tileset_path)
		self._pix = QPixmap(str(self._tileset_path.parent / self._tileset.image_path))
		self._tool: Tool = "pencil"
		self._layer = TileLayer(name="Layer 1", width=16, height=12, data=[-1] * (16 * 12))
		self._tilemap = Tilemap(
			tileset_path=str(self._tileset_path.relative_to(project.assets_dir)),
			tile_width=self._tileset.tile_width,
			tile_height=self._tileset.tile_height,
			layers=[self._layer],
		)

		main = QVBoxLayout(self)
		toolbar = QHBoxLayout()
		self._pencil_btn = QPushButton("Pencil", self)
		self._rect_btn = QPushButton("Rect", self)
		self._fill_btn = QPushButton("Fill", self)
		for b, t in (
			(self._pencil_btn, "pencil"),
			(self._rect_btn, "rect"),
			(self._fill_btn, "fill"),
		):
			b.setCheckable(True)
			b.clicked.connect(lambda checked=False, tool=t: self._set_tool(tool))
		toolbar.addWidget(self._pencil_btn)
		toolbar.addWidget(self._rect_btn)
		toolbar.addWidget(self._fill_btn)
		self._pencil_btn.setChecked(True)
		main.addLayout(toolbar)

		self._canvas = _TileCanvas(self)
		self._canvas.configure(self._pix, self._tilemap)
		main.addWidget(self._canvas)

		btns = QDialogButtonBox(self)
		self._save_btn = btns.addButton("Save Tilemap", QDialogButtonBox.ButtonRole.AcceptRole)
		btns.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
		btns.accepted.connect(self._on_save)
		btns.rejected.connect(self.reject)
		main.addWidget(btns)

	def _set_tool(self, tool: Tool) -> None:
		self._tool = tool
		self._canvas.set_tool(tool)

	def _on_save(self) -> None:
		# Persist tilemap json in scenes folder and add node to current scene via main window
		scene_dir = self._project.scenes_dir
		scene_dir.mkdir(parents=True, exist_ok=True)
		# name auto
		name = "tilemap"
		from json import dumps
		path = scene_dir / f"{name}.tilemap.json"
		path.write_text(dumps(self._tilemap.to_dict(), indent=2), encoding="utf-8")
		# Add node to hierarchy
		mw = self.window()
		try:
			node = TilemapNode(name="Tilemap")
			node.tilemap = self._tilemap
			mw._scene.add_child(mw._scene.root.id, node)  # type: ignore[attr-defined]
			mw.hierarchy_dock.refresh()  # type: ignore[attr-defined]
			mw._canvas.viewport().update()  # type: ignore[attr-defined]
		except Exception:
			pass
		self.accept()


class _TileCanvas(QLabel):  # type: ignore[misc]
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setMinimumSize(640, 480)
		self.setMouseTracking(True)
		self._pix = QPixmap()
		self._tilemap: Tilemap | None = None
		self._tool: Tool = "pencil"

	def configure(self, pix: QPixmap, tilemap: Tilemap) -> None:
		self._pix = pix
		self._tilemap = tilemap
		self._redraw()

	def set_tool(self, tool: Tool) -> None:
		self._tool = tool

	def mousePressEvent(self, ev: QMouseEvent) -> None:
		self._paint_at(ev)

	def mouseMoveEvent(self, ev: QMouseEvent) -> None:
		if ev.buttons() & Qt.MouseButton.LeftButton:
			self._paint_at(ev)

	def _paint_at(self, ev: QMouseEvent) -> None:
		if not self._tilemap:
			return
		pt = ev.pos()
		# map to tile coordinate assuming 1:1 preview scale for simplicity
		tw, th = self._tilemap.tile_width, self._tilemap.tile_height
		xi = max(0, min(self._tilemap.layers[0].width - 1, pt.x() // tw))
		yi = max(0, min(self._tilemap.layers[0].height - 1, pt.y() // th))
		idx = 0  # use first tile of tileset for now (stub)
		self._tilemap.layers[0].data[yi * self._tilemap.layers[0].width + xi] = idx
		self._redraw()

	def _redraw(self) -> None:
		if not self._tilemap:
			return
		canvas = QPixmap(self.width(), self.height())
		canvas.fill(Qt.GlobalColor.black)
		p = QPainter(canvas)
		for layer in self._tilemap.layers:
			for yi in range(layer.height):
				for xi in range(layer.width):
					idx = layer.data[yi * layer.width + xi]
					if idx < 0:
						continue
					x = xi * self._tilemap.tile_width
					y = yi * self._tilemap.tile_height
					p.fillRect(
						x,
						y,
						self._tilemap.tile_width,
						self._tilemap.tile_height,
						Qt.GlobalColor.darkGray,
					)
		p.end()
		self.setPixmap(canvas)


