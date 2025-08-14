from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QMouseEvent

from app.core.scene import Scene


@dataclass
class MoveState:
	start_pos: QPointF
	original_positions: dict[str, tuple[float, float]]


class MoveGizmo:
	def __init__(self, canvas, scene: Scene, get_snap_enabled) -> None:
		self.canvas = canvas
		self.scene = scene
		self.get_snap_enabled = get_snap_enabled
		self.state: MoveState | None = None

	def begin(self, event: QMouseEvent, selected_ids: Iterable[str]) -> None:
		pt = self.canvas.mapToScene(event.pos())
		self.state = MoveState(
			start_pos=pt,
			original_positions={sid: self._get_node_pos(sid) for sid in selected_ids},
		)

	def update(self, event: QMouseEvent) -> None:
		if not self.state:
			return
		pt = self.canvas.mapToScene(event.pos())
		dx = pt.x() - self.state.start_pos.x()
		dy = pt.y() - self.state.start_pos.y()
		snap = self.get_snap_enabled()
		for sid, (ox, oy) in self.state.original_positions.items():
			node = self.scene.find_node(sid)
			if not node:
				continue
			x, y = ox + dx, oy + dy
			sx, sy = self.canvas.snap_point(x, y, snap)
			node.transform.x = sx
			node.transform.y = sy
		self.canvas.viewport().update()

	def end(self) -> None:
		self.state = None

	def _get_node_pos(self, node_id: str) -> tuple[float, float]:
		node = self.scene.find_node(node_id)
		if not node:
			return 0.0, 0.0
		return float(node.transform.x), float(node.transform.y)


