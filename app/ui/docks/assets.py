from __future__ import annotations

from PyQt6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem


class AssetsDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Assets", parent)
		self.setObjectName("AssetsDock")
		self._tree = QTreeWidget(self)
		self._tree.setHeaderLabels(["Name"])
		self._tree.addTopLevelItem(QTreeWidgetItem(["assets/"]))
		self.setWidget(self._tree)


