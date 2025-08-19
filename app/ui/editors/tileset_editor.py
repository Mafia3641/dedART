from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from app.core.tilemap import Tileset


class TilesetEditor(QDialog):
	def __init__(self, tileset_path: Path, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Tileset Editor")
		self._path = tileset_path
		self._tileset = Tileset.load_json(tileset_path)
		self._pix = QPixmap(str(tileset_path.parent / self._tileset.image_path))

		main = QVBoxLayout(self)
		self._preview = QLabel(self)
		self._preview.setMinimumSize(400, 300)
		self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
		main.addWidget(self._preview)

		btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
		btns.rejected.connect(self.reject)
		btns.accepted.connect(self.accept)
		main.addWidget(btns)

		self._update_preview()

	def _update_preview(self) -> None:
		if self._pix.isNull():
			self._preview.setText("Image not found")
			return
		canvas = QPixmap(self._preview.size())
		canvas.fill(Qt.GlobalColor.black)
		p = QPainter(canvas)
		scaled = self._pix.scaled(
			self._preview.width(),
			self._preview.height(),
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation,
		)
		x = (self._preview.width() - scaled.width()) // 2
		y = (self._preview.height() - scaled.height()) // 2
		p.drawPixmap(x, y, scaled)
		p.setPen(QPen(Qt.GlobalColor.green, 1))
		# Простейшая сетка поверх (визуальная)
		if (
			self._tileset.tile_width > 0
			and self._tileset.tile_height > 0
			and scaled.width() > 0
			and scaled.height() > 0
		):
			sx = scaled.width() / max(1, self._tileset.image_width)
			sy = scaled.height() / max(1, self._tileset.image_height)
			step_x = int(self._tileset.tile_width * sx)
			step_y = int(self._tileset.tile_height * sy)
			cx = x
			while cx <= x + scaled.width():
				p.drawLine(cx, y, cx, y + scaled.height())
				cx += max(1, step_x)
			cy = y
			while cy <= y + scaled.height():
				p.drawLine(x, cy, x + scaled.width(), cy)
				cy += max(1, step_y)
		p.end()
		self._preview.setPixmap(canvas)


