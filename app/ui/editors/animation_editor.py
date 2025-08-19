from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import (
	QDialog,
	QDialogButtonBox,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QListWidget,
	QListWidgetItem,
	QPushButton,
	QSpinBox,
	QVBoxLayout,
)


class AnimationEditor(QDialog):
	"""Мини-редактор анимации спрайтов.

	Принимает путь к изображению (спрайт-лист) и список регионов кадров.
	Даёт предпросмотр анимации с заданным FPS.
	"""

	def __init__(
		self,
		image_path: str,
		frames: list[dict[str, int]] | None = None,
		fps: int = 8,
		parent=None,
	) -> None:
		super().__init__(parent)
		self.setWindowTitle("Animation Editor")
		self._pix = QPixmap(image_path)
		self._frames: list[dict[str, int]] = (
			frames[:] if frames else [
				{"x": 0, "y": 0, "w": self._pix.width(), "h": self._pix.height()}
			]
		)
		self._current_index = 0
		self._timer = QTimer(self)
		self._timer.timeout.connect(self._on_tick)

		# UI
		main = QVBoxLayout(self)
		self._preview = QLabel(self)
		self._preview.setMinimumSize(256, 256)
		self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
		main.addWidget(self._preview)

		controls = QGridLayout()
		main.addLayout(controls)

		self._list = QListWidget(self)
		self._list.currentRowChanged.connect(self._on_row_changed)
		controls.addWidget(QLabel("Frames:"), 0, 0)
		controls.addWidget(self._list, 1, 0, 4, 1)

		form = QGridLayout()
		controls.addLayout(form, 1, 1)
		self._sx = QSpinBox(self)
		self._sy = QSpinBox(self)
		self._sw = QSpinBox(self)
		self._sh = QSpinBox(self)
		self._sx.setRange(0, max(0, self._pix.width()))
		self._sy.setRange(0, max(0, self._pix.height()))
		self._sw.setRange(1, max(1, self._pix.width()))
		self._sh.setRange(1, max(1, self._pix.height()))
		form.addWidget(QLabel("X:"), 0, 0)
		form.addWidget(self._sx, 0, 1)
		form.addWidget(QLabel("Y:"), 1, 0)
		form.addWidget(self._sy, 1, 1)
		form.addWidget(QLabel("W:"), 2, 0)
		form.addWidget(self._sw, 2, 1)
		form.addWidget(QLabel("H:"), 3, 0)
		form.addWidget(self._sh, 3, 1)

		btns_row = QHBoxLayout()
		controls.addLayout(btns_row, 2, 1)
		self._add_btn = QPushButton("Add Frame", self)
		self._del_btn = QPushButton("Remove Frame", self)
		btns_row.addWidget(self._add_btn)
		btns_row.addWidget(self._del_btn)
		self._add_btn.clicked.connect(self._on_add)
		self._del_btn.clicked.connect(self._on_del)

		play_row = QHBoxLayout()
		main.addLayout(play_row)
		play_row.addWidget(QLabel("FPS:"))
		self._fps = QSpinBox(self)
		self._fps.setRange(1, 60)
		self._fps.setValue(max(1, fps))
		self._fps.valueChanged.connect(self._on_fps_changed)
		play_row.addWidget(self._fps)
		self._play_btn = QPushButton("Play", self)
		self._play_btn.clicked.connect(self._toggle_play)
		play_row.addWidget(self._play_btn)

		dlg_btns = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
			self,
		)
		dlg_btns.accepted.connect(self.accept)
		dlg_btns.rejected.connect(self.reject)
		main.addWidget(dlg_btns)

		self._rebuild_list()
		self._apply_row_to_spins(0)
		self._update_preview()
		self._apply_timer()

	def _rebuild_list(self) -> None:
		self._list.clear()
		for i, r in enumerate(self._frames):
			text = f"{i}: x={r['x']} y={r['y']} w={r['w']} h={r['h']}"
			QListWidgetItem(text, self._list)
		self._list.setCurrentRow(min(self._current_index, len(self._frames) - 1))

	def _apply_row_to_spins(self, idx: int) -> None:
		if 0 <= idx < len(self._frames):
			r = self._frames[idx]
			self._sx.setValue(int(r["x"]))
			self._sy.setValue(int(r["y"]))
			self._sw.setValue(int(r["w"]))
			self._sh.setValue(int(r["h"]))

	def _spins_region(self) -> dict[str, int]:
		return {
			"x": int(self._sx.value()),
			"y": int(self._sy.value()),
			"w": int(self._sw.value()),
			"h": int(self._sh.value()),
		}

	def _on_add(self) -> None:
		self._frames.append(self._spins_region())
		self._current_index = len(self._frames) - 1
		self._rebuild_list()
		self._update_preview()

	def _on_del(self) -> None:
		row = self._list.currentRow()
		if 0 <= row < len(self._frames):
			self._frames.pop(row)
			self._current_index = max(0, row - 1)
			self._rebuild_list()
			self._update_preview()

	def _on_row_changed(self, row: int) -> None:
		self._current_index = max(0, row)
		self._apply_row_to_spins(self._current_index)
		self._update_preview()

	def _on_fps_changed(self, value: int) -> None:
		self._apply_timer()

	def _toggle_play(self) -> None:
		if self._timer.isActive():
			self._timer.stop()
			self._play_btn.setText("Play")
		else:
			self._apply_timer()
			self._timer.start()
			self._play_btn.setText("Stop")

	def _apply_timer(self) -> None:
		fps = max(1, int(self._fps.value()))
		self._timer.setInterval(int(1000 / fps))

	def _on_tick(self) -> None:
		if not self._frames:
			return
		self._current_index = (self._current_index + 1) % len(self._frames)
		self._list.setCurrentRow(self._current_index)
		self._update_preview()

	def _current_frame_pixmap(self) -> QPixmap:
		if not self._frames:
			return QPixmap()
		r = self._frames[self._current_index]
		return self._pix.copy(int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"]))

	def _update_preview(self) -> None:
		frame = self._current_frame_pixmap()
		canvas = QPixmap(self._preview.size())
		canvas.fill(Qt.GlobalColor.black)
		if frame.isNull():
			self._preview.setPixmap(canvas)
			return
		p = QPainter(canvas)
		scaled = frame.scaled(
			self._preview.width(),
			self._preview.height(),
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation,
		)
		# центрируем
		x = (self._preview.width() - scaled.width()) // 2
		y = (self._preview.height() - scaled.height()) // 2
		p.drawPixmap(x, y, scaled)
		p.end()
		self._preview.setPixmap(canvas)

	def get_animation(self) -> dict[str, Any]:
		"""Вернуть описание анимации: fps и список кадров-регионов."""
		return {"fps": int(self._fps.value()), "frames": [dict(f) for f in self._frames]}


