from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings, Qt
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QApplication, QDialog, QDockWidget, QMainWindow

from app.core.commands import SetStatusMessageCommand, create_undo_stack
from app.core.project import create_new_project, open_project
from app.core.settings import add_recent_project, load_settings, save_settings
from app.ui.canvas import CanvasView
from app.ui.dialogs.new_project import NewProjectDialog
from app.ui.docks.assets import AssetsDock
from app.ui.docks.console import ConsoleDock
from app.ui.docks.hierarchy import HierarchyDock
from app.ui.docks.inspector import InspectorDock


class MainWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("dedART Editor")

		# Menus: File, Edit, View, Help
		menu_bar = self.menuBar()
		self.file_menu = menu_bar.addMenu("File")
		self.edit_menu = menu_bar.addMenu("Edit")
		view_menu = menu_bar.addMenu("View")
		self._action_theme_light = QAction("Light", self)
		self._action_theme_dark = QAction("Dark", self)
		self._theme_group = QActionGroup(self)
		self._theme_group.setExclusive(True)
		for act in (self._action_theme_light, self._action_theme_dark):
			act.setCheckable(True)
			self._theme_group.addAction(act)
		view_menu.addAction(self._action_theme_light)
		view_menu.addAction(self._action_theme_dark)
		self._panels_menu = view_menu.addMenu("Panels")
		menu_bar.addMenu("Help")


		# Central canvas
		self._canvas = CanvasView(self)
		self.setCentralWidget(self._canvas)

		# Docks
		self.hierarchy_dock = HierarchyDock(self)
		self.inspector_dock = InspectorDock(self)
		self.assets_dock = AssetsDock(self)
		self.console_dock = ConsoleDock(self)


		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.hierarchy_dock)
		self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)
		self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)
		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.assets_dock)

		# Assets — слева снизу. Для этого создаём разделитель с hierarchy и кладём assets вниз
		self.splitDockWidget(self.hierarchy_dock, self.assets_dock, Qt.Orientation.Vertical)
		self.assets_dock.setFloating(False)

		# Panels toggles
		self._register_panel_toggle("Hierarchy", self.hierarchy_dock)
		self._register_panel_toggle("Inspector", self.inspector_dock)
		self._register_panel_toggle("Assets", self.assets_dock)
		self._register_panel_toggle("Console", self.console_dock)

		# Status bar
		self.statusBar().showMessage("Ready")

		# Undo stack
		self.undo_stack = create_undo_stack(self)
		self._add_edit_actions()
		self._add_file_actions()

		# Create an empty scene and show in hierarchy
		from app.core.scene import Scene
		self._scene = Scene(name="Untitled")
		self.hierarchy_dock.set_scene(self._scene)

		# Restore layout
		self._settings = QSettings("dedART", "Editor")
		self._restore_dock_layout()

		# Theme toggle state
		settings = load_settings()
		is_dark = settings.theme != "light"
		self._action_theme_dark.setChecked(is_dark)
		self._action_theme_light.setChecked(not is_dark)
		self._action_theme_dark.triggered.connect(lambda: self._on_theme_changed("dark"))
		self._action_theme_light.triggered.connect(lambda: self._on_theme_changed("light"))
		# Demo command to test Undo/Redo
		demo = QAction("Set status to 'Hello'", self)
		demo.triggered.connect(self._demo_set_status)
		self.edit_menu.addAction(demo)

	def closeEvent(self, event):  # type: ignore[override]
		self._save_dock_layout()
		super().closeEvent(event)

	def _restore_dock_layout(self) -> None:
		geometry: QByteArray | None = self._settings.value("main/geometry")
		state: QByteArray | None = self._settings.value("main/state")
		if geometry is not None:
			self.restoreGeometry(geometry)
		if state is not None:
			self.restoreState(state)

	def _save_dock_layout(self) -> None:
		self._settings.setValue("main/geometry", self.saveGeometry())
		self._settings.setValue("main/state", self.saveState())

	def _add_edit_actions(self) -> None:
		undo_action = self.undo_stack.createUndoAction(self, "Undo")
		undo_action.setShortcut("Ctrl+Z")
		redo_action = self.undo_stack.createRedoAction(self, "Redo")
		redo_action.setShortcut("Ctrl+Y")
		self.edit_menu.addAction(undo_action)
		self.edit_menu.addAction(redo_action)

	def _register_panel_toggle(self, title: str, dock: QDockWidget) -> None:
		action = QAction(title, self)
		action.setCheckable(True)
		action.setChecked(dock.isVisible())
		action.triggered.connect(lambda checked, d=dock: d.setVisible(checked))
		dock.visibilityChanged.connect(lambda vis, a=action: a.setChecked(vis))
		self._panels_menu.addAction(action)

	def _add_file_actions(self) -> None:
		new_project_action = QAction("New Project…", self)
		new_project_action.triggered.connect(self._action_new_project)
		open_project_action = QAction("Open Project…", self)
		open_project_action.triggered.connect(self._action_open_project)
		self.file_menu.addAction(new_project_action)
		self.file_menu.addAction(open_project_action)
		self.file_menu.addSeparator()
		self._recent_menu = self.file_menu.addMenu("Recent Projects")
		self._rebuild_recent_menu()

	def _demo_set_status(self) -> None:
		self.undo_stack.push(SetStatusMessageCommand(self, "Hello"))

	def _on_theme_changed(self, theme: str) -> None:
		app = QApplication.instance()
		if app is not None:
			base = Path(__file__).resolve().parent / "themes"
			file = base / ("dark.qss" if theme == "dark" else "light.qss")
			try:
				app.setStyleSheet(file.read_text(encoding="utf-8"))
			except Exception:
				app.setStyleSheet("")
		settings = load_settings()
		settings.theme = theme
		save_settings(settings)

	def _action_new_project(self) -> None:
		dlg = NewProjectDialog(self)
		if dlg.exec() == QDialog.DialogCode.Accepted:  # type: ignore[attr-defined]
			values = dlg.get_values()
			if values is None:
				return
			root, name, w, h = values
			project = create_new_project(root, name, w, h)
			self.statusBar().showMessage(f"Project created: {project.root}")
			add_recent_project(str(project.root))
			self._rebuild_recent_menu()

	def _action_open_project(self) -> None:
		from PyQt6.QtWidgets import QFileDialog

		path = QFileDialog.getExistingDirectory(self, "Open Project")
		if not path:
			return
		try:
			project = open_project(Path(path))
			self.statusBar().showMessage(f"Project opened: {project.root}")
			add_recent_project(str(project.root))
			self._rebuild_recent_menu()
		except Exception as e:
			self.statusBar().showMessage(f"Failed to open: {e}")

	def _rebuild_recent_menu(self) -> None:
		self._recent_menu.clear()
		settings = load_settings()
		for p in settings.recent_projects:
			a = QAction(p, self)
			a.triggered.connect(lambda checked=False, path=p: self._open_recent(path))
			self._recent_menu.addAction(a)

	def _open_recent(self, path: str) -> None:
		try:
			project = open_project(Path(path))
			self.statusBar().showMessage(f"Project opened: {project.root}")
			add_recent_project(str(project.root))
			self._rebuild_recent_menu()
		except Exception as e:
			self.statusBar().showMessage(f"Failed to open: {e}")


