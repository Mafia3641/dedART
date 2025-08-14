from __future__ import annotations

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
