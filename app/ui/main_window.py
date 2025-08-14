from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings, Qt
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QApplication, QDialog, QDockWidget, QMainWindow

from app.core.commands import (
	DeleteNodesCommand,
	PasteNodesCommand,
	SetStatusMessageCommand,
	create_undo_stack,
)
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

		# Current project holder
		self._project = None

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
		self._grid_menu = view_menu.addMenu("Grid")
		self._action_grid_toggle = QAction("Show Grid", self)
		self._action_grid_toggle.setCheckable(True)
		self._action_snap_toggle = QAction("Snap to Grid", self)
		self._action_snap_toggle.setCheckable(True)
		self._action_grid_step_16 = QAction("Step 16", self)
		self._action_grid_step_32 = QAction("Step 32", self)
		self._action_grid_step_64 = QAction("Step 64", self)
		for a in (self._action_grid_step_16, self._action_grid_step_32, self._action_grid_step_64):
			a.setCheckable(True)
		self._grid_group = QActionGroup(self)
		self._grid_group.setExclusive(True)
		for a in (self._action_grid_step_16, self._action_grid_step_32, self._action_grid_step_64):
			self._grid_group.addAction(a)
		self._grid_menu.addAction(self._action_grid_toggle)
		self._grid_menu.addAction(self._action_snap_toggle)
		self._grid_menu.addSeparator()
		self._grid_menu.addAction(self._action_grid_step_16)
		self._grid_menu.addAction(self._action_grid_step_32)
		self._grid_menu.addAction(self._action_grid_step_64)
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
		self._canvas.set_scene(self._scene)
		self.hierarchy_dock.selection_changed.connect(self._canvas.set_selected_ids)
		self._canvas.selection_changed.connect(self.hierarchy_dock.set_selected_ids)  # type: ignore[attr-defined]
		self.inspector_dock.set_scene(self._scene)
		self.hierarchy_dock.selection_changed.connect(self.inspector_dock.set_selected_ids)
		# Assets dock receives current project root (if any)
		self.assets_dock.set_project(None)
		# Hook to create sprite from Assets on double click
		self.create_sprite_from_asset = self._create_sprite_from_asset  # type: ignore[assignment]

		# Move gizmo wiring (basic): begin with Ctrl+Left, drag to move, release to finish
		from app.ui.tools.move_gizmo import MoveGizmo  # noqa: I001
		from PyQt6.QtCore import QObject  # noqa: I001

		self._move_gizmo = MoveGizmo(
			self._canvas,
			self._scene,
			lambda: load_settings().snap_to_grid,
		)

		class _CanvasProxy(QObject):
			def __init__(self, outer):
				super().__init__(outer)
				self.outer = outer
				outer._canvas.mousePressEvent_orig = outer._canvas.mousePressEvent
				outer._canvas.mouseMoveEvent_orig = outer._canvas.mouseMoveEvent
				outer._canvas.mouseReleaseEvent_orig = outer._canvas.mouseReleaseEvent

			def mousePressEvent(self, ev):
				mods = ev.modifiers()
				is_ctrl = bool(mods & Qt.KeyboardModifier.ControlModifier)
				if ev.button() == Qt.MouseButton.LeftButton and is_ctrl:
					self.outer._move_gizmo.begin(ev, self.outer._canvas._selected_ids)
					return
				return self.outer._canvas.mousePressEvent_orig(ev)

			def mouseMoveEvent(self, ev):
				if self.outer._move_gizmo.state is not None:
					self.outer._move_gizmo.update(ev)
					return
				return self.outer._canvas.mouseMoveEvent_orig(ev)

			def mouseReleaseEvent(self, ev):
				is_left = ev.button() == Qt.MouseButton.LeftButton
				if self.outer._move_gizmo.state is not None and is_left:
					self.outer._move_gizmo.end()
					return
				return self.outer._canvas.mouseReleaseEvent_orig(ev)

		proxy = _CanvasProxy(self)
		self._canvas.mousePressEvent = proxy.mousePressEvent  # type: ignore[assignment]
		self._canvas.mouseMoveEvent = proxy.mouseMoveEvent  # type: ignore[assignment]
		self._canvas.mouseReleaseEvent = proxy.mouseReleaseEvent  # type: ignore[assignment]

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
		# Grid initial
		self._action_grid_toggle.setChecked(settings.grid_enabled)
		self._action_snap_toggle.setChecked(settings.snap_to_grid)
		self._set_grid_step_checked(settings.grid_step)
		self._action_grid_toggle.toggled.connect(self._on_grid_toggled)
		self._action_snap_toggle.toggled.connect(self._on_snap_toggled)
		self._action_grid_step_16.triggered.connect(lambda: self._on_grid_step(16))
		self._action_grid_step_32.triggered.connect(lambda: self._on_grid_step(32))
		self._action_grid_step_64.triggered.connect(lambda: self._on_grid_step(64))
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

	def _setup_edit_shortcuts(self) -> None:
		from PyQt6.QtGui import QKeySequence, QShortcut

		delete_sc = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
		delete_sc.activated.connect(self._action_delete_selection)
		copy_sc = QShortcut(QKeySequence.StandardKey.Copy, self)
		copy_sc.activated.connect(self._action_copy_selection)
		paste_sc = QShortcut(QKeySequence.StandardKey.Paste, self)
		paste_sc.activated.connect(self._action_paste_selection)

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

		# Edit shortcuts for delete/copy/paste
		self._setup_edit_shortcuts()

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

	def _on_grid_toggled(self, enabled: bool) -> None:
		settings = load_settings()
		settings.grid_enabled = enabled
		save_settings(settings)
		self._canvas.set_grid(enabled)

	def _on_grid_step(self, step: int) -> None:
		settings = load_settings()
		settings.grid_step = step
		save_settings(settings)
		self._canvas.set_grid(self._action_grid_toggle.isChecked(), step)
		self._set_grid_step_checked(step)

	def _on_snap_toggled(self, enabled: bool) -> None:
		settings = load_settings()
		settings.snap_to_grid = enabled
		save_settings(settings)

	def _set_grid_step_checked(self, step: int) -> None:
		mapping = {
			16: self._action_grid_step_16,
			32: self._action_grid_step_32,
			64: self._action_grid_step_64,
		}
		for s, action in mapping.items():
			action.setChecked(s == step)

	def _set_current_project(self, project) -> None:
		# Replace current project context: assets, future scene loading here
		self._project = project
		self.assets_dock.set_project(project)
		# TODO: load last scene from project.json in future tasks

	def _create_sprite_from_asset(self, image_path: str, region: dict | None = None) -> None:
		# Create a sprite node via command for Undo/Redo
		from app.core.commands import CreateSpriteCommand

		self.undo_stack.push(CreateSpriteCommand(self._scene, self._scene.root.id, image_path))
		# If region provided, set on last created node (simple approach)
		if region:
			# naive: attach to last child of root
			if self._scene.root.children:
				self._scene.root.children[-1].sprite_region = region
		self.hierarchy_dock.refresh()
		self._canvas.viewport().update()

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
			self.assets_dock.set_project(project)
			self.assets_dock._import_btn.setEnabled(True)

	def _action_open_project(self) -> None:
		from PyQt6.QtWidgets import QFileDialog

		path = QFileDialog.getExistingDirectory(self, "Open Project")
		if not path:
			return
		try:
			project = open_project(Path(path))
			self._set_current_project(project)
			self.statusBar().showMessage(f"Project opened: {project.root}")
			add_recent_project(str(project.root))
			self._rebuild_recent_menu()
			self.assets_dock._import_btn.setEnabled(True)
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
			self._set_current_project(project)
			self.statusBar().showMessage(f"Project opened: {project.root}")
			add_recent_project(str(project.root))
			self._rebuild_recent_menu()
		except Exception as e:
			self.statusBar().showMessage(f"Failed to open: {e}")

	def _get_selection_ids(self) -> list[str]:
		return list(self._canvas._selected_ids)

	def _action_delete_selection(self) -> None:
		ids = [nid for nid in self._get_selection_ids() if nid != self._scene.root.id]
		if not ids:
			return
		self.undo_stack.push(DeleteNodesCommand(self._scene, ids))
		self.hierarchy_dock.refresh()
		self._canvas.viewport().update()

	def _action_copy_selection(self) -> None:
		from PyQt6.QtWidgets import QApplication

		ids = self._get_selection_ids()
		if not ids:
			return
		data: list[dict] = []
		for nid in ids:
			node = self._scene.find_node(nid)
			if node:
				data.append(node.to_dict())
		QApplication.clipboard().setText(json.dumps(data))

	def _action_paste_selection(self) -> None:
		from PyQt6.QtWidgets import QApplication

		text = QApplication.clipboard().text()
		try:
			items = json.loads(text)
		except Exception:
			return
		if not isinstance(items, list):
			return
		parent_ids = self.hierarchy_dock.get_selected_ids()
		parent_id = parent_ids[0] if parent_ids else self._scene.root.id
		self.undo_stack.push(PasteNodesCommand(self._scene, parent_id, items))
		self.hierarchy_dock.refresh()
		self._canvas.viewport().update()


