from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path

from PIL import Image

from app.core.project import Project

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_image_file(path: Path) -> bool:
	return path.suffix.lower() in IMAGE_EXTENSIONS


def import_images(project: Project, sources: Iterable[Path]) -> list[Path]:
	project.assets_dir.mkdir(parents=True, exist_ok=True)
	result: list[Path] = []
	for src in sources:
		src = src.expanduser().resolve()
		if not src.exists() or not is_image_file(src):
			continue
		dst = project.assets_dir / src.name
		# If name collision, add numeric suffix
		counter = 1
		while dst.exists():
			stem, suf = dst.stem, dst.suffix
			dst = project.assets_dir / f"{stem}_{counter}{suf}"
			counter += 1
		shutil.copy2(src, dst)
		result.append(dst)
		try:
			_generate_thumbnail(dst)
		except Exception:
			pass
	return result


def _generate_thumbnail(image_path: Path, size: int = 96) -> Path:
	thumb_dir = image_path.parent / ".thumbnails"
	thumb_dir.mkdir(exist_ok=True)
	thumb_path = thumb_dir / f"{image_path.stem}_thumb.png"
	with Image.open(image_path) as im:
		im.thumbnail((size, size))
		im.convert("RGBA").save(thumb_path, format="PNG")
	return thumb_path


