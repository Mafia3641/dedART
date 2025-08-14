from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Transform:
	x: float = 0.0
	y: float = 0.0
	rotation_deg: float = 0.0
	scale_x: float = 1.0
	scale_y: float = 1.0

	def to_dict(self) -> dict[str, Any]:
		return {
			"x": self.x,
			"y": self.y,
			"rotation_deg": self.rotation_deg,
			"scale_x": self.scale_x,
			"scale_y": self.scale_y,
		}

	@staticmethod
	def from_dict(data: dict[str, Any]) -> Transform:
		return Transform(
			x=float(data.get("x", 0.0)),
			y=float(data.get("y", 0.0)),
			rotation_deg=float(data.get("rotation_deg", 0.0)),
			scale_x=float(data.get("scale_x", 1.0)),
			scale_y=float(data.get("scale_y", 1.0)),
		)


@dataclass
class Node:
	name: str
	id: str = field(default_factory=lambda: str(uuid.uuid4()))
	transform: Transform = field(default_factory=Transform)
	sprite_path: str | None = None
	sprite_region: dict | None = None  # {x,y,w,h}
	children: list[Node] = field(default_factory=list)

	def add_child(self, node: Node) -> None:
		self.children.append(node)

	def to_dict(self) -> dict[str, Any]:
		return {
			"id": self.id,
			"name": self.name,
			"transform": self.transform.to_dict(),
			"sprite_path": self.sprite_path,
			"sprite_region": self.sprite_region,
			"children": [child.to_dict() for child in self.children],
		}

	@staticmethod
	def from_dict(data: dict[str, Any]) -> Node:
		node = Node(
			name=str(data.get("name", "Node")),
			id=str(data.get("id", str(uuid.uuid4()))),
			transform=Transform.from_dict(data.get("transform", {})),
		)
		node.sprite_path = data.get("sprite_path") or None
		node.sprite_region = data.get("sprite_region") or None
		for child_data in data.get("children", []) or []:
			node.children.append(Node.from_dict(child_data))
		return node


@dataclass
class Scene:
	name: str
	root: Node = field(default_factory=lambda: Node(name="Root"))

	def to_dict(self) -> dict[str, Any]:
		return {
			"name": self.name,
			"root": self.root.to_dict(),
		}

	@staticmethod
	def from_dict(data: dict[str, Any]) -> Scene:
		return Scene(
			name=str(data.get("name", "Scene")),
			root=Node.from_dict(data.get("root", {"name": "Root"})),
		)

	def save_json(self, path: Path) -> None:
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

	@staticmethod
	def load_json(path: Path) -> Scene:
		data = json.loads(path.read_text(encoding="utf-8"))
		return Scene.from_dict(data)

	# Utilities
	def find_node(self, node_id: str, start: Node | None = None) -> Node | None:
		start = start or self.root
		if start.id == node_id:
			return start
		for child in start.children:
			found = self.find_node(node_id, child)
			if found:
				return found
		return None

	def add_child(self, parent_id: str, node: Node) -> bool:
		parent = self.find_node(parent_id)
		if parent is None:
			return False
		parent.add_child(node)
		return True

	def remove_node(self, node_id: str, start: Node | None = None) -> bool:
		start = start or self.root
		for idx, child in enumerate(start.children):
			if child.id == node_id:
				del start.children[idx]
				return True
			if self.remove_node(node_id, child):
				return True
		return False


