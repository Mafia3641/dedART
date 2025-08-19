from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class Tileset:
	image_path: str
	tile_width: int
	tile_height: int
	image_width: int
	image_height: int
	columns: int
	rows: int

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)

	@staticmethod
	def from_image(image_path: Path, tile_width: int, tile_height: int) -> Tileset:
		with Image.open(image_path) as im:
			img_w, img_h = im.size
		columns = max(1, img_w // max(1, tile_width))
		rows = max(1, img_h // max(1, tile_height))
		return Tileset(
			image_path=str(image_path.name),
			tile_width=int(tile_width),
			tile_height=int(tile_height),
			image_width=int(img_w),
			image_height=int(img_h),
			columns=int(columns),
			rows=int(rows),
		)

	def save_json(self, target: Path) -> Path:
		target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
		return target

	@staticmethod
	def load_json(path: Path) -> Tileset:
		data = json.loads(path.read_text(encoding="utf-8"))
		return Tileset(
			image_path=str(data.get("image_path", "")),
			tile_width=int(data.get("tile_width", 32)),
			tile_height=int(data.get("tile_height", 32)),
			image_width=int(data.get("image_width", 0)),
			image_height=int(data.get("image_height", 0)),
			columns=int(data.get("columns", 0)),
			rows=int(data.get("rows", 0)),
		)


def create_tileset_metadata(assets_dir: Path, image_path: Path, tile_w: int, tile_h: int) -> Path:
	"""Create tileset metadata JSON next to the image in assets directory.

	Returns path to created json file.
	"""
	if not image_path.exists():
		raise FileNotFoundError(image_path)
	if image_path.parent != assets_dir:
		raise ValueError("image must be inside assets directory")
	tileset = Tileset.from_image(image_path, tile_w, tile_h)
	json_path = image_path.with_suffix("")
	json_path = json_path.with_name(f"{json_path.name}.tileset.json")
	return tileset.save_json(json_path)


def list_tilesets(assets_dir: Path) -> list[Path]:
	"""Return list of tileset metadata files in assets directory."""
	if not assets_dir.exists():
		return []
	return sorted(
		[
			p
			for p in assets_dir.iterdir()
			if p.is_file() and p.name.endswith(".tileset.json")
		]
	)


# --- Tilemap structures ---


@dataclass
class TileLayer:
	name: str
	width: int
	height: int
	data: list[int]

	def to_dict(self) -> dict[str, Any]:
		return {
			"name": self.name,
			"width": int(self.width),
			"height": int(self.height),
			"data": list(self.data),
		}

	@staticmethod
	def from_dict(data: dict[str, Any]) -> TileLayer:
		return TileLayer(
			name=str(data.get("name", "Layer 1")),
			width=int(data.get("width", 0)),
			height=int(data.get("height", 0)),
			data=[int(x) for x in (data.get("data") or [])],
		)


@dataclass
class Tilemap:
	tileset_path: str
	tile_width: int
	tile_height: int
	layers: list[TileLayer]

	def to_dict(self) -> dict[str, Any]:
		return {
			"tileset_path": self.tileset_path,
			"tile_width": int(self.tile_width),
			"tile_height": int(self.tile_height),
			"layers": [layer.to_dict() for layer in self.layers],
		}

	@staticmethod
	def from_dict(data: dict[str, Any]) -> Tilemap:
		return Tilemap(
			tileset_path=str(data.get("tileset_path", "")),
			tile_width=int(data.get("tile_width", 32)),
			tile_height=int(data.get("tile_height", 32)),
			layers=[TileLayer.from_dict(ld) for ld in (data.get("layers") or [])],
		)

	def tile_source_rect(self, index: int, tileset: Tileset) -> tuple[int, int, int, int]:
		"""Return source rect (x,y,w,h) for tile index in tileset grid."""
		if index < 0:
			return 0, 0, 0, 0
		cols = max(1, tileset.columns)
		x = (index % cols) * self.tile_width
		y = (index // cols) * self.tile_height
		return x, y, self.tile_width, self.tile_height


