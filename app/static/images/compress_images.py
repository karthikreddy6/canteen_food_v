"""Resize images in this folder to 300x300 and skip unchanged files.

Install once:
    python -m pip install Pillow

Run from this folder:
    python compress_images.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps


FOLDER = Path(__file__).resolve().parent
STATE_FILE = FOLDER / ".compressed_images.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
SIZE = (300, 300)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_state() -> dict[str, str]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def compress(path: Path) -> None:
    with Image.open(path) as image:
        # Fit/crop gives every output the exact requested 300x300 dimensions.
        image = ImageOps.fit(image.convert("RGB"), SIZE, method=Image.Resampling.LANCZOS)

        # Keep PNG files as PNG; save other supported formats as JPEG.
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            image.save(path, format="JPEG", quality=85, optimize=True, progressive=True)
        elif path.suffix.lower() == ".webp":
            image.save(path, format="WEBP", quality=85, method=6)
        else:
            image.save(path, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compress new images to exactly 300x300 pixels.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="process every image again and rebuild the tracking list",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be processed without changing images",
    )
    args = parser.parse_args()

    state = {} if args.force else load_state()
    images = sorted(
        path for path in FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    processed = 0
    skipped = 0
    for path in images:
        relative_name = path.name
        current_hash = sha256(path)

        if not args.force and state.get(relative_name) == current_hash:
            print(f"Skipped: {relative_name}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"Would compress: {relative_name}")
            continue

        try:
            compress(path)
            state[relative_name] = sha256(path)
            print(f"Compressed: {relative_name}")
            processed += 1
        except (OSError, ValueError) as error:
            print(f"Failed: {relative_name} ({error})")

    if not args.dry_run:
        # Remove entries for images that no longer exist.
        state = {path.name: state[path.name] for path in images if path.name in state}
        save_state(state)

    print(f"Done. Compressed: {processed}; skipped: {skipped}; found: {len(images)}")


if __name__ == "__main__":
    main()
