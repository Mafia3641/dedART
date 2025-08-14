from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMenu, QTreeWidget, QTreeWidgetItem

from app.core.scene import Node, Scene


class HierarchyDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Hierarchy", parent)
		self.setObjectName("HierarchyDock")
		self._tree = QTreeWidget(self)
		self._tree.setHeaderLabels(["Name"]) 
		self.setWidget(self._tree)
		self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self._tree.customContextMenuRequested.connect(self._on_context_menu)
		self._scene: Scene | None = None

	def set_scene(self, scene: Scene) -> None:
		self._scene = scene
		self._rebuild()

	def _rebuild(self) -> None:
		self._tree.clear()
		if not self._scene:
			return
		root_item = self._node_to_item(self._scene.root)
		self._tree.addTopLevelItem(root_item)
		self._tree.expandAll()

	def _node_to_item(self, node: Node) -> QTreeWidgetItem:
		item = QTreeWidgetItem([node.name])
		item.setData(0, 0, node.id)  # store id for later
		for child in node.children:
			item.addChild(self._node_to_item(child))
		return item

	def _on_context_menu(self, pos) -> None:
		if not self._scene:
			return
		from app.core.commands import AddNodeCommand, RemoveNodeCommand

		global_pos = self._tree.viewport().mapToGlobal(pos)
		item = self._tree.itemAt(pos)
		node_id = item.data(0, 0) if item else self._scene.root.id
		menu = QMenu(self)
		act_add = menu.addAction("Add Child")
		act_remove = None
		if item and node_id != self._scene.root.id:
			act_remove = menu.addAction("Remove")
		chosen = menu.exec(global_pos)
		if not chosen:
			return
		# Find main window to access undo_stack and refresh
		from PyQt6.QtWidgets import QMainWindow
		mw: QMainWindow | None = self.window()  # type: ignore[assignment]
		if chosen == act_add and mw is not None:
			mw.undo_stack.push(AddNodeCommand(self._scene, node_id, "Node"))  # type: ignore[arg-type]
			self._rebuild()
		elif act_remove and chosen == act_remove and mw is not None:
			mw.undo_stack.push(RemoveNodeCommand(self._scene, node_id))  # type: ignore[arg-type]
			self._rebuild()


