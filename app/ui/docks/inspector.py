from __future__ import annotations

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
from PyQt6.QtWidgets import (
	QDockWidget,
	QDoubleSpinBox,
	QFormLayout,
	QLineEdit,
	QWidget,
)

from app.core.commands import SetNodeNameCommand, SetTransformFieldCommand
from app.core.scene import Scene


class InspectorDock(QDockWidget):
	selection_changed = pyqtSignal(list)

	def __init__(self, parent=None) -> None:
		super().__init__("Inspector", parent)
		self.setObjectName("InspectorDock")
		self._scene: Scene | None = None
		self._selected_ids: list[str] = []

		self._container = QWidget(self)
		self._form = QFormLayout(self._container)
		self._last_field_values: dict[str, float] = {
			"x": 0.0,
			"y": 0.0,
			"rotation_deg": 0.0,
			"scale_x": 1.0,
			"scale_y": 1.0,
		}

		self._name_edit = QLineEdit(self._container)
		self._name_edit.editingFinished.connect(self._on_name_changed)

		self._pos_x = QDoubleSpinBox(self._container)
		self._pos_y = QDoubleSpinBox(self._container)
		self._rot = QDoubleSpinBox(self._container)
		self._scale_x = QDoubleSpinBox(self._container)
		self._scale_y = QDoubleSpinBox(self._container)
		for sb in (self._pos_x, self._pos_y, self._rot, self._scale_x, self._scale_y):
			sb.setRange(-1e6, 1e6)
			sb.setDecimals(3)

		self._pos_x.valueChanged.connect(
			lambda _=0.0: self._on_field_changed("x", float(self._pos_x.value()))
		)
		self._pos_y.valueChanged.connect(
			lambda _=0.0: self._on_field_changed("y", float(self._pos_y.value()))
		)
		self._rot.valueChanged.connect(
			lambda _=0.0: self._on_field_changed(
				"rotation_deg", float(self._rot.value())
			)
		)
		self._scale_x.valueChanged.connect(
			lambda _=0.0: self._on_field_changed("scale_x", float(self._scale_x.value()))
		)
		self._scale_y.valueChanged.connect(
			lambda _=0.0: self._on_field_changed("scale_y", float(self._scale_y.value()))
		)

		self._form.addRow("Name:", self._name_edit)
		self._form.addRow("X:", self._pos_x)
		self._form.addRow("Y:", self._pos_y)
		self._form.addRow("Rotation (deg):", self._rot)
		self._form.addRow("Scale X:", self._scale_x)
		self._form.addRow("Scale Y:", self._scale_y)
		self._container.setLayout(self._form)
		self.setWidget(self._container)

	def set_scene(self, scene: Scene) -> None:
		self._scene = scene
		self._refresh()

	def set_selected_ids(self, ids: list[str]) -> None:
		self._selected_ids = ids
		self._refresh()

	def _refresh(self) -> None:
		if not self._scene or not self._selected_ids:
			self._name_edit.setText("")
			self._pos_x.setValue(0.0)
			self._pos_y.setValue(0.0)
			self._rot.setValue(0.0)
			self._scale_x.setValue(1.0)
			self._scale_y.setValue(1.0)
			for w in (
				self._name_edit,
				self._pos_x,
				self._pos_y,
				self._rot,
				self._scale_x,
				self._scale_y,
			):
				w.setEnabled(False)
			return
		# Если выделено несколько — показываем поля по первому, но изменения будем применять ко всем
		first = self._scene.find_node(self._selected_ids[0])
		if not first:
			return
		self._name_edit.setEnabled(True)
		self._pos_x.setEnabled(True)
		self._pos_y.setEnabled(True)
		self._rot.setEnabled(True)
		self._scale_x.setEnabled(True)
		self._scale_y.setEnabled(True)
		# Блокируем сигналы на время обновления UI, чтобы не применять дельты самопроизвольно
		bx = QSignalBlocker(self._pos_x)
		by = QSignalBlocker(self._pos_y)
		br = QSignalBlocker(self._rot)
		bsx = QSignalBlocker(self._scale_x)
		bsy = QSignalBlocker(self._scale_y)
		self._name_edit.setText(first.name)
		self._pos_x.setValue(float(first.transform.x))
		self._pos_y.setValue(float(first.transform.y))
		self._rot.setValue(float(first.transform.rotation_deg))
		self._scale_x.setValue(float(first.transform.scale_x))
		self._scale_y.setValue(float(first.transform.scale_y))
		del bx, by, br, bsx, bsy
		# Обновляем базовые значения для расчёта дельт в мультивыборе
		self._last_field_values["x"] = float(first.transform.x)
		self._last_field_values["y"] = float(first.transform.y)
		self._last_field_values["rotation_deg"] = float(first.transform.rotation_deg)
		self._last_field_values["scale_x"] = float(first.transform.scale_x)
		self._last_field_values["scale_y"] = float(first.transform.scale_y)

	def _on_name_changed(self) -> None:
		if not self._scene or not self._selected_ids:
			return
		new_name = self._name_edit.text().strip()
		if not new_name:
			return
		self.parent().undo_stack.push(  # type: ignore[attr-defined]
			SetNodeNameCommand(self._scene, self._selected_ids[0], new_name)
		)

	def _on_field_changed(self, field: str, value: float) -> None:
		if not self._scene or not self._selected_ids:
			return
		if len(self._selected_ids) == 1:
			# Обычное поведение — абсолютное присваивание
			node_id = self._selected_ids[0]
			self.parent().undo_stack.push(  # type: ignore[attr-defined]
				SetTransformFieldCommand(self._scene, node_id, field, float(value))
			)
		else:
			# Мультивыбор — применяем относительную дельту ко всем объектам
			delta = float(value) - float(self._last_field_values.get(field, 0.0))
			if abs(delta) < 1e-9:
				return
			for node_id in self._selected_ids:
				node = self._scene.find_node(node_id)
				if not node:
					continue
				current = getattr(node.transform, field)
				new_val = float(current) + delta
				self.parent().undo_stack.push(  # type: ignore[attr-defined]
					SetTransformFieldCommand(self._scene, node_id, field, new_val)
				)
			# Обновляем базовое значение на показанное в UI
			self._last_field_values[field] = float(value)
		try:
			self.parent()._canvas.viewport().update()  # type: ignore[attr-defined]
		except Exception:
			pass


