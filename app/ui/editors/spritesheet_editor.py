from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
	QDialog,
	QDialogButtonBox,
	QHBoxLayout,
	QLabel,
	QSpinBox,
	QVBoxLayout,
)


class SpritesheetEditor(QDialog):
	def __init__(self, image_path: str, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Spritesheet Editor")
		self._pix = QPixmap(image_path)
		self._x = 0
		self._y = 0
		self._w = min(64, self._pix.width())
		self._h = min(64, self._pix.height())

		layout = QVBoxLayout(self)
		self._preview = QLabel(self)
		self._preview.setMinimumSize(256, 256)
		layout.addWidget(self._preview)

		row = QHBoxLayout()
		self._sx = QSpinBox(self)
		self._sx.setRange(0, max(0, self._pix.width() - 1))
		self._sx.valueChanged.connect(self._update)
		self._sy = QSpinBox(self)
		self._sy.setRange(0, max(0, self._pix.height() - 1))
		self._sy.valueChanged.connect(self._update)
		self._sw = QSpinBox(self)
		self._sw.setRange(1, self._pix.width())
		self._sw.setValue(self._w)
		self._sw.valueChanged.connect(self._update)
		self._sh = QSpinBox(self)
		self._sh.setRange(1, self._pix.height())
		self._sh.setValue(self._h)
		self._sh.valueChanged.connect(self._update)
		row.addWidget(QLabel("X:"))
		row.addWidget(self._sx)
		row.addWidget(QLabel("Y:"))
		row.addWidget(self._sy)
		row.addWidget(QLabel("W:"))
		row.addWidget(self._sw)
		row.addWidget(QLabel("H:"))
		row.addWidget(self._sh)
		layout.addLayout(row)

		buttons = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
			self,
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		layout.addWidget(buttons)

		self._update()

	def _update(self) -> None:
		self._x = self._sx.value()
		self._y = self._sy.value()
		self._w = self._sw.value()
		self._h = self._sh.value()
		canvas = QPixmap(self._preview.size())
		canvas.fill(Qt.GlobalColor.black)
		p = QPainter(canvas)
		scaled = self._pix.scaled(
			self._preview.width(),
			self._preview.height(),
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation,
		)
		p.drawPixmap(0, 0, scaled)
		p.setPen(QPen(Qt.GlobalColor.red, 2))
		scale_x = self._preview.width() / max(1, self._pix.width())
		scale_y = self._preview.height() / max(1, self._pix.height())
		rect = QRect(
			int(self._x * scale_x),
			int(self._y * scale_y),
			int(self._w * scale_x),
			int(self._h * scale_y),
		)
		p.drawRect(rect)
		p.end()
		self._preview.setPixmap(canvas)

	def get_region(self) -> dict:
		return {"x": int(self._x), "y": int(self._y), "w": int(self._w), "h": int(self._h)}


