from __future__ import annotations

from PyQt6.QtCore import QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QMouseEvent, QPainter, QPen, QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView


class CanvasView(QGraphicsView):
	selection_changed = pyqtSignal(list)
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._scene = QGraphicsScene(self)
		self.setScene(self._scene)
		self.setRenderHints(QPainter.RenderHint.Antialiasing)
		self.setDragMode(QGraphicsView.DragMode.NoDrag)
		self._panning = False
		self._last_pan_pos = QPoint()
		self._zoom = 1.0
		self._grid_enabled = True
		self._grid_step = 32
		self._scene_model = None
		self._selected_ids: list[str] = []
		self._rubber_active = False
		self._rubber_start = None
		self._rubber_end = None

	def set_scene(self, scene_model) -> None:
		self._scene_model = scene_model
		self.viewport().update()

	def wheelEvent(self, event):  # type: ignore[override]
		if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
			delta = event.angleDelta().y()
			factor = 1.0015 ** delta
			self._zoom *= factor
			self.scale(factor, factor)
			return
		super().wheelEvent(event)

	def mousePressEvent(self, event: QMouseEvent):  # type: ignore[override]
		if event.button() == Qt.MouseButton.MiddleButton:
			self._panning = True
			self._last_pan_pos = event.pos()
			self.setCursor(Qt.CursorShape.ClosedHandCursor)
			return
		if event.button() == Qt.MouseButton.LeftButton:
			self._rubber_active = True
			self._rubber_start = self.mapToScene(event.pos())
			self._rubber_end = self._rubber_start
			return
		super().mousePressEvent(event)

	def mouseMoveEvent(self, event: QMouseEvent):  # type: ignore[override]
		if self._panning:
			delta = event.pos() - self._last_pan_pos
			self._last_pan_pos = event.pos()
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
			return
		if self._rubber_active:
			self._rubber_end = self.mapToScene(event.pos())
			self.viewport().update()
			return
		super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event: QMouseEvent):  # type: ignore[override]
		if event.button() == Qt.MouseButton.MiddleButton:
			self._panning = False
			self.setCursor(Qt.CursorShape.ArrowCursor)
			return
		if event.button() == Qt.MouseButton.LeftButton and self._rubber_active:
			self._rubber_active = False
			self._apply_selection(event)
			self._rubber_start = None
			self._rubber_end = None
			self.viewport().update()
			return
		super().mouseReleaseEvent(event)

	def set_selection_callback(self, callback) -> None:
		self.selection_changed = callback

	def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # type: ignore[override]
		super().drawBackground(painter, rect)
		if not self._grid_enabled:
			return
		painter.save()
		painter.setPen(QPen(Qt.GlobalColor.gray, 0))
		step = max(4, self._grid_step)
		left = int(rect.left()) - (int(rect.left()) % step)
		top = int(rect.top()) - (int(rect.top()) % step)
		x = left
		while x < rect.right():
			painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
			x += step
		y = top
		while y < rect.bottom():
			painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
			y += step
		painter.restore()

	def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # type: ignore[override]
		super().drawForeground(painter, rect)
		# Draw nodes: sprites as textures with transform; others as small rects
		if self._scene_model is not None:
			painter.save()
			for node in self._iterate_nodes(self._scene_model.root):
				pos_x = float(getattr(node.transform, 'x', 0.0))
				pos_y = float(getattr(node.transform, 'y', 0.0))
				rot = float(getattr(node.transform, 'rotation_deg', 0.0))
				sx = float(getattr(node.transform, 'scale_x', 1.0))
				sy = float(getattr(node.transform, 'scale_y', 1.0))
				is_sel = node.id in self._selected_ids
				painter.save()
				painter.translate(pos_x, pos_y)
				if rot:
					painter.rotate(rot)
				if sx != 1.0 or sy != 1.0:
					painter.scale(sx, sy)
				# Tilemap rendering
				if hasattr(node, 'tilemap') and node.tilemap is not None:
					self._draw_tilemap_node(painter, node)
					painter.restore()
					continue
				tex_path = getattr(node, 'sprite_path', None)
				if tex_path:
					pix = QPixmap(str(tex_path))
					if not pix.isNull():
						region = getattr(node, 'sprite_region', None)
						if (
							isinstance(region, dict)
							and all(k in region for k in ("x", "y", "w", "h"))
						):
							pix = pix.copy(
								int(region["x"]),
								int(region["y"]),
								int(region["w"]),
								int(region["h"]),
							)
						w = pix.width()
						h = pix.height()
						painter.drawPixmap(-w // 2, -h // 2, pix)
						if is_sel:
							painter.setPen(QPen(Qt.GlobalColor.cyan, 0))
							painter.drawRect(-w // 2, -h // 2, w, h)
						painter.restore()
						continue
				# fallback marker
				size = 6
				painter.setPen(QPen(Qt.GlobalColor.cyan if is_sel else Qt.GlobalColor.darkCyan, 0))
				painter.setBrush(QBrush(Qt.GlobalColor.cyan if is_sel else Qt.GlobalColor.darkCyan))
				painter.drawRect(int(-size / 2), int(-size / 2), size, size)
				painter.restore()
			painter.restore()
		# Draw rubber band
		if self._rubber_active and self._rubber_start and self._rubber_end:
			painter.save()
			painter.setPen(QPen(Qt.GlobalColor.blue, 0, Qt.PenStyle.DashLine))
			r = self._make_rect(self._rubber_start, self._rubber_end)
			painter.drawRect(r)
			painter.restore()

	def set_grid(self, enabled: bool, step: int | None = None) -> None:
		self._grid_enabled = enabled
		if step is not None:
			self._grid_step = step
		self.viewport().update()

	def set_selected_ids(self, ids: list[str]) -> None:
		self._selected_ids = list(ids)
		self.viewport().update()

	def _iterate_nodes(self, start):
		yield start
		for child in start.children:
			yield from self._iterate_nodes(child)

	def _make_rect(self, a, b) -> QRectF:
		left = min(a.x(), b.x())
		top = min(a.y(), b.y())
		return QRectF(left, top, abs(a.x() - b.x()), abs(a.y() - b.y()))

	def _apply_selection(self, event: QMouseEvent) -> None:
		if self._scene_model is None:
			return
		mods = event.modifiers()
		additive = bool(mods & Qt.KeyboardModifier.ShiftModifier)
		selected_list: list[str] = list(self._selected_ids) if additive else []
		selected_set: set[str] = set(selected_list)
		# Rubber-band or single-click depending on rectangle size
		if self._rubber_start and self._rubber_end:
			selection_rect = self._make_rect(self._rubber_start, self._rubber_end)
			is_click = selection_rect.width() <= 2 and selection_rect.height() <= 2
		else:
			selection_rect = None
			is_click = True

		if not is_click and selection_rect is not None:
			for node in self._iterate_nodes(self._scene_model.root):
				local_rect, world_transform = self._node_local_rect_and_transform(node)
				world_rect = world_transform.mapRect(local_rect)
				if world_rect.intersects(selection_rect) and node.id not in selected_set:
					selected_list.append(node.id)
					selected_set.add(node.id)
		else:
			# Single click: pick topmost under cursor
			pt = self.mapToScene(event.pos())
			picked: str | None = None
			# collect nodes to list to iterate in reverse draw order
			nodes = list(self._iterate_nodes(self._scene_model.root))
			for node in reversed(nodes):
				local_rect, world_transform = self._node_local_rect_and_transform(node)
				inv, ok = world_transform.inverted()
				if not ok:
					continue
				pt_local = inv.map(pt)
				if local_rect.contains(pt_local):
					picked = node.id
					break
			if picked is not None:
				if additive and picked in selected_set:
					selected_list = [nid for nid in selected_list if nid != picked]
					selected_set.discard(picked)
				else:
					selected_list = ([picked] if not additive else selected_list + [picked])
					selected_set.add(picked)
		self._selected_ids = selected_list
		self.selection_changed.emit(list(self._selected_ids))

	def _node_local_rect_and_transform(self, node):
		# Compute local rect centered at origin and world transform for a node
		pos_x = float(getattr(node.transform, 'x', 0.0))
		pos_y = float(getattr(node.transform, 'y', 0.0))
		rot = float(getattr(node.transform, 'rotation_deg', 0.0))
		sx = float(getattr(node.transform, 'scale_x', 1.0))
		sy = float(getattr(node.transform, 'scale_y', 1.0))
		tex_path = getattr(node, 'sprite_path', None)
		if tex_path:
			pix = QPixmap(str(tex_path))
			if not pix.isNull():
				region = getattr(node, 'sprite_region', None)
				if (
					isinstance(region, dict)
					and all(k in region for k in ("x", "y", "w", "h"))
				):
					pix = pix.copy(
						int(region["x"]),
						int(region["y"]),
						int(region["w"]),
						int(region["h"]),
					)
				w = max(1, pix.width())
				h = max(1, pix.height())
				local_rect = QRectF(-w / 2, -h / 2, w, h)
				transform = QTransform()
				transform.translate(pos_x, pos_y)
				if rot:
					transform.rotate(rot)
				if sx != 1.0 or sy != 1.0:
					transform.scale(sx, sy)
				return local_rect, transform
		# fallback small square
		size = 6.0
		local_rect = QRectF(-size / 2, -size / 2, size, size)
		transform = QTransform()
		transform.translate(pos_x, pos_y)
		if rot:
			transform.rotate(rot)
		if sx != 1.0 or sy != 1.0:
			transform.scale(sx, sy)
		return local_rect, transform

	def _draw_tilemap_node(self, painter: QPainter, node) -> None:
		# Basic single-layer render from tileset image
		tilemap = node.tilemap
		if tilemap is None or self._scene_model is None:
			return
		# Resolve tileset image path using project assets dir if available
		from app.core.tilemap import Tileset

		assets_dir = getattr(getattr(self, '_current_project', None), 'assets_dir', None)
		# Fallback: nothing to draw without assets dir
		if assets_dir is None:
			return
		ts_path = (assets_dir / tilemap.tileset_path).resolve()
		try:
			ts = Tileset.load_json(ts_path)
		except Exception:
			return
		img_path = ts_path.parent / ts.image_path
		pix = QPixmap(str(img_path))
		if pix.isNull():
			return
		for layer in tilemap.layers:
			w = layer.width
			h = layer.height
			for yi in range(h):
				for xi in range(w):
					idx = layer.data[yi * w + xi] if yi * w + xi < len(layer.data) else -1
					if idx < 0:
						continue
					sx, sy, tw, th = tilemap.tile_source_rect(idx, ts)
					src = pix.copy(int(sx), int(sy), int(tw), int(th))
					painter.drawPixmap(int(xi * tw - tw // 2), int(yi * th - th // 2), src)

	def snap_point(self, x: float, y: float, snap: bool) -> tuple[float, float]:
		if not snap:
			return x, y
		step = max(1, self._grid_step)
		return round(x / step) * step, round(y / step) * step


