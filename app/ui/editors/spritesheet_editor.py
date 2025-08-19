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
		self._w = self._pix.width()
		self._h = self._pix.height()

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
		row.addWidget(QLabel("X:"))
		row.addWidget(self._sw)
		row.addWidget(QLabel("Y:"))
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
		# Compute uniform scale to fit while keeping aspect
		view_w = max(1, self._preview.width())
		view_h = max(1, self._preview.height())
		img_w = max(1, self._pix.width())
		img_h = max(1, self._pix.height())
		scale = min(view_w / img_w, view_h / img_h)
		scaled_w = int(img_w * scale)
		scaled_h = int(img_h * scale)
		offset_x = (view_w - scaled_w) // 2
		offset_y = (view_h - scaled_h) // 2
		scaled_pix = self._pix.scaled(
			scaled_w,
			scaled_h,
			Qt.AspectRatioMode.IgnoreAspectRatio,
			Qt.TransformationMode.SmoothTransformation,
		)
		p.drawPixmap(offset_x, offset_y, scaled_pix)
		p.setPen(QPen(Qt.GlobalColor.red, 2))
		rect = QRect(
			int(offset_x + self._x * scale),
			int(offset_y + self._y * scale),
			int(self._w * scale),
			int(self._h * scale),
		)
		p.drawRect(rect)
		p.end()
		self._preview.setPixmap(canvas)

	def get_region(self) -> dict:
		return {"x": int(self._x), "y": int(self._y), "w": int(self._w), "h": int(self._h)}


