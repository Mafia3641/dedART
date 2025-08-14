from __future__ import annotations

from PyQt6.QtWidgets import QDockWidget, QTextEdit


class ConsoleDock(QDockWidget):
	def __init__(self, parent=None) -> None:
		super().__init__("Console", parent)
		self.setObjectName("ConsoleDock")
		self._text = QTextEdit(self)
		self._text.setReadOnly(True)
		self._text.setPlainText("Console output will appear here")
		self.setWidget(self._text)


