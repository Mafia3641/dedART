from __future__ import annotations

from PyQt6.QtWidgets import (
	QDockWidget,
	QLabel,
	QVBoxLayout,
	QWidget,
)


class InspectorDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Inspector", parent)
		self.setObjectName("InspectorDock")
		container = QWidget(self)
		layout = QVBoxLayout(container)
		layout.addWidget(QLabel("Inspector (placeholder)", container))
		container.setLayout(layout)
		self.setWidget(container)


