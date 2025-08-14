from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
	QDialog,
	QDialogButtonBox,
	QFileDialog,
	QFormLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QSpinBox,
	QVBoxLayout,
)


class NewProjectDialog(QDialog):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("New Project")

		self.path_edit = QLineEdit(self)
		self.name_edit = QLineEdit(self)
		self.width_spin = QSpinBox(self)
		self.height_spin = QSpinBox(self)
		self.width_spin.setRange(64, 16384)
		self.height_spin.setRange(64, 16384)
		self.width_spin.setValue(1920)
		self.height_spin.setValue(1080)

		browse_btn = QPushButton("Browse…", self)
		browse_btn.clicked.connect(self._browse)

		form = QFormLayout()
		row = QHBoxLayout()
		row.addWidget(self.path_edit)
		row.addWidget(browse_btn)
		form.addRow("Location:", row)
		form.addRow("Name:", self.name_edit)
		form.addRow("Scene width:", self.width_spin)
		form.addRow("Scene height:", self.height_spin)

		buttons = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
			parent=self,
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		layout = QVBoxLayout(self)
		layout.addLayout(form)
		layout.addWidget(buttons)
		self.setLayout(layout)

	def _browse(self) -> None:
		path = QFileDialog.getExistingDirectory(self, "Select Location")
		if path:
			self.path_edit.setText(path)

	def get_values(self) -> tuple[Path, str, int, int] | None:
		root = Path(self.path_edit.text()).expanduser().resolve()
		name = self.name_edit.text().strip()
		if not root or not name:
			return None
		return root / name, name, int(self.width_spin.value()), int(self.height_spin.value())


