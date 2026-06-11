# /// script
# dependencies = [
#     "pillow>=10.0.0",
# ]
# ///

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "public" / "candidates"
SIZE = 256


def resize_png(path: Path) -> None:
    with Image.open(path) as img:
        resized = img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        resized.save(path, format="PNG")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resize PNGs under a directory to 256x256 in place.",
    )
    parser.add_argument(
        "dir",
        nargs="?",
        default=DEFAULT_DIR,
        type=Path,
        help="Directory to scan (default: public/candidates)",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        raise SystemExit(f"error: directory not found: {args.dir}")

    pngs = sorted(args.dir.rglob("*.png"))
    for png in pngs:
        resize_png(png)

    print(f"resized {len(pngs)} PNGs in {args.dir} to {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
