from __future__ import annotations

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView


class CanvasView(QGraphicsView):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._scene = QGraphicsScene(self)
		self.setScene(self._scene)


