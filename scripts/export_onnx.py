"""CLI utility for exporting a trained YOLO model to ONNX."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.exceptions import ConfigError, RailScanError  # noqa: E402


@dataclass(frozen=True)
class ExportSettings:
    weights: Path
    format: str
    imgsz: int
    opset: int
    output: Path
    dry_run: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export RailScan YOLO weights to ONNX.")
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--format")
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--opset", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_settings(args: argparse.Namespace, config: Mapping[str, Any]) -> ExportSettings:
    export_config = config.get("export", {})
    if not isinstance(export_config, Mapping):
        raise ConfigError("Config section 'export' must be a mapping.")

    return ExportSettings(
        weights=_resolve_path(
            args.weights
            if args.weights is not None
            else export_config.get("weights", "runs/train/railscan_yolo/weights/best.pt")
        ),
        format=str(args.format or export_config.get("format", "onnx")).lower(),
        imgsz=_positive_int(
            args.imgsz if args.imgsz is not None else export_config.get("imgsz", 320),
            "imgsz",
        ),
        opset=_positive_int(
            args.opset if args.opset is not None else export_config.get("opset", 12),
            "opset",
        ),
        output=_resolve_path(
            args.output
            if args.output is not None
            else export_config.get("output", "models/railscan_yolo.onnx")
        ),
        dry_run=bool(args.dry_run),
    )


def validate_settings(settings: ExportSettings, *, require_weights: bool) -> None:
    if settings.format != "onnx":
        raise ConfigError("Prompt 7 export supports format='onnx' only.")
    if settings.output.suffix.lower() != ".onnx":
        raise ConfigError(f"Export output must use .onnx suffix: {settings.output}")

    if require_weights:
        if not settings.weights.exists():
            raise ConfigError(f"YOLO weights not found: {settings.weights}")
        if not settings.weights.is_file():
            raise ConfigError(f"YOLO weights path is not a file: {settings.weights}")
        if settings.weights.suffix.lower() != ".pt":
            raise ConfigError(f"YOLO weights must use .pt suffix: {settings.weights}")


def print_settings(settings: ExportSettings) -> None:
    print("YOLO export configuration:")
    print(f"  weights: {settings.weights}")
    print(f"  format: {settings.format}")
    print(f"  imgsz: {settings.imgsz}")
    print(f"  opset: {settings.opset}")
    print(f"  output: {settings.output}")


def run_export(settings: ExportSettings) -> Path:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ConfigError(
            "ultralytics is required for real export. "
            "Install requirements-train.txt first."
        ) from exc

    settings.output.parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(settings.weights))
    exported_path = Path(
        model.export(
            format=settings.format,
            imgsz=settings.imgsz,
            opset=settings.opset,
        )
    )

    if exported_path.resolve() != settings.output.resolve():
        shutil.copy2(exported_path, settings.output)

    return settings.output


def main() -> int:
    args = parse_args()

    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
        settings = build_settings(args, config)
        validate_settings(settings, require_weights=not settings.dry_run)
        print_settings(settings)

        if settings.dry_run:
            print("Dry run: ONNX export was not started.")
            return 0

        output = run_export(settings)

    except RailScanError as exc:
        print(f"ONNX export failed: {exc}", file=sys.stderr)
        return 1

    print(f"ONNX export completed successfully: {output}")
    return 0


def _resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _positive_int(value: Any, key: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Export value {key!r} must be an integer.") from exc

    if parsed <= 0:
        raise ConfigError(f"Export value {key!r} must be greater than zero.")

    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
