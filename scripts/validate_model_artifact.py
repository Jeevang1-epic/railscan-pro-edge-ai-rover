"""Validate the expected RailScan ONNX model artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate RailScan model artifact.")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models") / "railscan_yolo.onnx",
    )
    parser.add_argument("--allow-missing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_path = _resolve_path(args.model)

    if model_path.suffix.lower() != ".onnx":
        print(f"Model artifact must use .onnx suffix: {model_path}", file=sys.stderr)
        return 1

    if not model_path.exists():
        if args.allow_missing:
            print(f"Model artifact is missing but allowed: {model_path}")
            return 0
        print(f"Model artifact not found: {model_path}", file=sys.stderr)
        return 1

    if not model_path.is_file():
        print(f"Model artifact path is not a file: {model_path}", file=sys.stderr)
        return 1

    size_bytes = model_path.stat().st_size
    if size_bytes <= 0:
        print(f"Model artifact is empty: {model_path}", file=sys.stderr)
        return 1

    print(f"Model artifact found: {model_path}")
    print(f"Model artifact size bytes: {size_bytes}")
    return 0


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
