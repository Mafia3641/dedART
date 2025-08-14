from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QUndoCommand, QUndoStack
from PyQt6.QtWidgets import QMainWindow

from app.core.scene import Node, Scene


def create_undo_stack(parent) -> QUndoStack:
	return QUndoStack(parent)


class SetStatusMessageCommand(QUndoCommand):
	def __init__(self, window: QMainWindow, new_message: str) -> None:
		super().__init__("Set Status Message")
		self._window = window
		self._new_message = new_message
		self._prev_message: str | None = None

	def redo(self) -> None:  # type: ignore[override]
		if self._prev_message is None:
			self._prev_message = self._window.statusBar().currentMessage()
		self._window.statusBar().showMessage(self._new_message)

	def undo(self) -> None:  # type: ignore[override]
		self._window.statusBar().showMessage(self._prev_message or "")


class AddNodeCommand(QUndoCommand):
	def __init__(self, scene: Scene, parent_id: str, node_name: str) -> None:
		super().__init__(f"Add Node: {node_name}")
		self._scene = scene
		self._parent_id = parent_id
		self._node = Node(name=node_name)

	def redo(self) -> None:  # type: ignore[override]
		self._scene.add_child(self._parent_id, self._node)

	def undo(self) -> None:  # type: ignore[override]
		self._scene.remove_node(self._node.id)


class RemoveNodeCommand(QUndoCommand):
	def __init__(self, scene: Scene, node_id: str) -> None:
		super().__init__("Remove Node")
		self._scene = scene
		self._node_id = node_id
		self._parent_id: str | None = None
		self._snapshot: Node | None = None

	def redo(self) -> None:  # type: ignore[override]
		# Find parent and snapshot
		if self._snapshot is None:
			self._snapshot = self._scene.find_node(self._node_id)
			# Find parent by DFS
			self._parent_id = self._find_parent_id(self._scene.root, self._node_id)
		self._scene.remove_node(self._node_id)

	def undo(self) -> None:  # type: ignore[override]
		if self._snapshot and self._parent_id:
			self._scene.add_child(self._parent_id, self._snapshot)

	def _find_parent_id(self, start: Node, child_id: str) -> str | None:
		for child in start.children:
			if child.id == child_id:
				return start.id
			found = self._find_parent_id(child, child_id)
			if found:
				return found
		return None


class DeleteNodesCommand(QUndoCommand):
	def __init__(self, scene: Scene, node_ids: list[str]) -> None:
		super().__init__("Delete Nodes")
		self._scene = scene
		self._node_ids = self._filter_top_level(node_ids)
		self._snapshots: list[tuple[str, Node]] = []  # (parent_id, node)

	def redo(self) -> None:  # type: ignore[override]
		if not self._snapshots:
			for nid in self._node_ids:
				parent_id = self._find_parent_id(self._scene.root, nid)
				if parent_id is None:
					continue
				node = self._scene.find_node(nid)
				if node is None:
					continue
				self._snapshots.append((parent_id, node))
		for nid in self._node_ids:
			self._scene.remove_node(nid)

	def undo(self) -> None:  # type: ignore[override]
		for parent_id, node in self._snapshots:
			self._scene.add_child(parent_id, node)

	def _filter_top_level(self, ids: list[str]) -> list[str]:
		id_set = set(ids)
		result: list[str] = []
		for nid in ids:
			cur = self._find_parent_id(self._scene.root, nid)
			top = True
			while cur is not None:
				if cur in id_set:
					top = False
					break
				cur = self._find_parent_id(self._scene.root, cur)
			if top:
				result.append(nid)
		return result

	def _find_parent_id(self, start: Node, child_id: str) -> str | None:
		for child in start.children:
			if child.id == child_id:
				return start.id
			found = self._find_parent_id(child, child_id)
			if found:
				return found
		return None


def _clone_node_with_new_ids(node: Node) -> Node:
	copy = Node(name=node.name)
	copy.transform = node.transform  # shallow copy; acceptable for demo
	for child in node.children:
		copy.children.append(_clone_node_with_new_ids(child))
	return copy


class PasteNodesCommand(QUndoCommand):
	def __init__(self, scene: Scene, parent_id: str, nodes_data: list[dict]) -> None:
		super().__init__("Paste Nodes")
		self._scene = scene
		self._parent_id = parent_id
		self._nodes_data = nodes_data
		self.created_ids: list[str] = []

	def redo(self) -> None:  # type: ignore[override]
		from app.core.scene import Node

		self.created_ids.clear()
		for nd in self._nodes_data:
			node = Node.from_dict(nd)
			node = _clone_node_with_new_ids(node)
			self._scene.add_child(self._parent_id, node)
			self.created_ids.append(node.id)

	def undo(self) -> None:  # type: ignore[override]
		for nid in self.created_ids:
			self._scene.remove_node(nid)


class CreateSpriteCommand(QUndoCommand):
    def __init__(self, scene: Scene, parent_id: str, sprite_path: str, name: str | None = None,
                 pos_x: float | None = None, pos_y: float | None = None) -> None:
        super().__init__("Create Sprite")
        self._scene = scene
        self._parent_id = parent_id
        self._sprite_path = sprite_path
        self._name = name or f"Sprite:{Path(sprite_path).name}"
        self._pos_x = pos_x
        self._pos_y = pos_y
        self.created_id: str | None = None

    def redo(self) -> None:  # type: ignore[override]
        from app.core.scene import Node

        node = Node(name=self._name)
        node.sprite_path = self._sprite_path
        if self._pos_x is not None:
            node.transform.x = float(self._pos_x)
        if self._pos_y is not None:
            node.transform.y = float(self._pos_y)
        self._scene.add_child(self._parent_id, node)
        self.created_id = node.id

    def undo(self) -> None:  # type: ignore[override]
        if self.created_id:
            self._scene.remove_node(self.created_id)


class SetNodeNameCommand(QUndoCommand):
	def __init__(self, scene: Scene, node_id: str, new_name: str) -> None:
		super().__init__("Rename Node")
		self._scene = scene
		self._node_id = node_id
		self._new = new_name
		self._old: str | None = None

	def redo(self) -> None:  # type: ignore[override]
		node = self._scene.find_node(self._node_id)
		if not node:
			return
		if self._old is None:
			self._old = node.name
		node.name = self._new

	def undo(self) -> None:  # type: ignore[override]
		node = self._scene.find_node(self._node_id)
		if not node or self._old is None:
			return
		node.name = self._old


class SetTransformFieldCommand(QUndoCommand):
	def __init__(self, scene: Scene, node_id: str, field: str, new_value: float) -> None:
		super().__init__(f"Set {field}")
		self._scene = scene
		self._node_id = node_id
		self._field = field
		self._new = float(new_value)
		self._old: float | None = None

	def redo(self) -> None:  # type: ignore[override]
		node = self._scene.find_node(self._node_id)
		if not node:
			return
		cur = getattr(node.transform, self._field, 0.0)
		if self._old is None:
			self._old = float(cur)
		setattr(node.transform, self._field, self._new)

	def undo(self) -> None:  # type: ignore[override]
		node = self._scene.find_node(self._node_id)
		if not node or self._old is None:
			return
		setattr(node.transform, self._field, self._old)
