from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

PROJECT_DIRNAME = ".gameproj"
PROJECT_FILE = "project.json"


@dataclass
class ProjectMeta:
	name: str
	version: int = 1
	scene_width: int = 1920
	scene_height: int = 1080


@dataclass
class Project:
	root: Path
	meta: ProjectMeta

	@property
	def project_dir(self) -> Path:
		return self.root / PROJECT_DIRNAME

	@property
	def assets_dir(self) -> Path:
		return self.root / "assets"

	@property
	def scenes_dir(self) -> Path:
		return self.root / "scenes"

	def save(self) -> None:
		self.project_dir.mkdir(parents=True, exist_ok=True)
		self.assets_dir.mkdir(parents=True, exist_ok=True)
		self.scenes_dir.mkdir(parents=True, exist_ok=True)
		data = {
			"name": self.meta.name,
			"version": self.meta.version,
			"scene": {"width": self.meta.scene_width, "height": self.meta.scene_height},
		}
		(self.project_dir / PROJECT_FILE).write_text(
			json.dumps(data, indent=2), encoding="utf-8"
		)

	@staticmethod
	def load(root: Path) -> Project:
		project_file = root / PROJECT_DIRNAME / PROJECT_FILE
		data = json.loads(project_file.read_text(encoding="utf-8"))
		name = data.get("name", root.name)
		version = int(data.get("version", 1))
		scene = data.get("scene", {})
		meta = ProjectMeta(
			name=name,
			version=version,
			scene_width=int(scene.get("width", 1920)),
			scene_height=int(scene.get("height", 1080)),
		)
		return Project(root=root, meta=meta)


def create_new_project(root: Path, name: str, scene_width: int, scene_height: int) -> Project:
	project = Project(
		root=root,
		meta=ProjectMeta(
			name=name,
			scene_width=scene_width,
			scene_height=scene_height,
		),
	)
	project.save()
	return project


def validate_project(root: Path) -> bool:
	return (root / PROJECT_DIRNAME / PROJECT_FILE).exists()


def open_project(root: Path) -> Project:
	if not validate_project(root):
		raise FileNotFoundError(f"Invalid project structure: {root}")
	return Project.load(root)


def save_project(project: Project) -> None:
	project.save()


def save_project_as(project: Project, new_root: Path) -> Project:
	new = Project(root=new_root, meta=project.meta)
	new.save()
	return new


# Scene helpers
def scene_path(project: Project, scene_name: str) -> Path:
	return project.scenes_dir / f"{scene_name}.json"


if TYPE_CHECKING:  # pragma: no cover
	from app.core.scene import Scene


def save_scene(project: Project, scene: Scene) -> Path:
    path = scene_path(project, scene.name)
    scene.save_json(path)
    return path


def load_scene(project: Project, scene_name: str) -> Scene:
    from app.core.scene import Scene

    return Scene.load_json(scene_path(project, scene_name))

