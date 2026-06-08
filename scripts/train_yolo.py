"""CLI utility for YOLO training configuration and launch."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.exceptions import ConfigError, RailScanError  # noqa: E402

DATASET_SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class TrainingSettings:
    data: Path
    model: str
    imgsz: int
    epochs: int
    batch: int
    project: Path
    name: str
    device: str
    dry_run: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a RailScan YOLO detector.")
    parser.add_argument("--data", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--imgsz", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--device")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_settings(args: argparse.Namespace, config: Mapping[str, Any]) -> TrainingSettings:
    training_config = config.get("training", {})
    if not isinstance(training_config, Mapping):
        raise ConfigError("Config section 'training' must be a mapping.")

    return TrainingSettings(
        data=_resolve_path(
            args.data
            if args.data is not None
            else training_config.get("data", "datasets/railscan_v1/data.yaml")
        ),
        model=str(args.model or training_config.get("base_model", "yolo11n.pt")),
        imgsz=_positive_int(
            args.imgsz if args.imgsz is not None else training_config.get("imgsz", 320),
            "imgsz",
        ),
        epochs=_positive_int(
            args.epochs
            if args.epochs is not None
            else training_config.get("epochs", 50),
            "epochs",
        ),
        batch=_positive_int(
            args.batch if args.batch is not None else training_config.get("batch", 16),
            "batch",
        ),
        project=_resolve_path(
            args.project
            if args.project is not None
            else training_config.get("project", "runs/train")
        ),
        name=str(args.name or training_config.get("name", "railscan_yolo")),
        device=str(args.device or training_config.get("device", "auto")),
        dry_run=bool(args.dry_run),
    )


def validate_dataset(
    settings: TrainingSettings,
    *,
    require_folders: bool,
    expected_class_names: Sequence[str] = (),
) -> list[str]:
    if not settings.data.exists():
        raise ConfigError(f"Dataset YAML not found: {settings.data}")
    if not settings.data.is_file():
        raise ConfigError(f"Dataset YAML path is not a file: {settings.data}")
    if settings.data.suffix.lower() not in {".yaml", ".yml"}:
        raise ConfigError(f"Dataset config must be a YAML file: {settings.data}")

    try:
        dataset_config = yaml.safe_load(settings.data.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Dataset YAML is invalid: {settings.data}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read dataset YAML: {settings.data}") from exc

    if not isinstance(dataset_config, Mapping):
        raise ConfigError("Dataset YAML root must be a mapping.")

    _validate_dataset_paths(dataset_config)

    names = dataset_config.get("names")
    class_names = _read_class_names(names)
    if not class_names:
        raise ConfigError("Dataset YAML must define at least one class name.")

    nc = _positive_int(dataset_config.get("nc"), "nc")
    if nc != len(class_names):
        raise ConfigError(
            "Dataset YAML nc must match the number of class names."
        )

    if expected_class_names and tuple(expected_class_names) != class_names:
        raise ConfigError(
            "Dataset class names must match config model.class_names order."
        )

    dataset_root = _dataset_root(settings.data, dataset_config)
    warnings: list[str] = []
    for relative_dir in (
        "images/train",
        "images/val",
        "labels/train",
        "labels/val",
        "images/test",
        "labels/test",
    ):
        folder = dataset_root / relative_dir
        if not folder.exists():
            message = f"Dataset folder missing: {folder}"
            if require_folders:
                raise ConfigError(message)
            warnings.append(message)

    return warnings


def print_settings(settings: TrainingSettings, warnings: list[str]) -> None:
    print("YOLO training configuration:")
    print(f"  data: {settings.data}")
    print(f"  model: {settings.model}")
    print(f"  imgsz: {settings.imgsz}")
    print(f"  epochs: {settings.epochs}")
    print(f"  batch: {settings.batch}")
    print(f"  project: {settings.project}")
    print(f"  name: {settings.name}")
    print(f"  device: {settings.device}")
    for warning in warnings:
        print(f"  warning: {warning}")


def run_training(settings: TrainingSettings) -> None:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ConfigError(
            "ultralytics is required for real training. "
            "Install requirements-train.txt first."
        ) from exc

    train_kwargs: dict[str, Any] = {
        "data": str(settings.data),
        "imgsz": settings.imgsz,
        "epochs": settings.epochs,
        "batch": settings.batch,
        "project": str(settings.project),
        "name": settings.name,
    }
    if settings.device.lower() != "auto":
        train_kwargs["device"] = settings.device

    model = YOLO(settings.model)
    model.train(**train_kwargs)


def main() -> int:
    args = parse_args()

    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
        settings = build_settings(args, config)
        warnings = validate_dataset(
            settings,
            require_folders=not settings.dry_run,
            expected_class_names=_config_class_names(config),
        )
        print_settings(settings, warnings)

        if settings.dry_run:
            print("Dry run: YOLO training was not started.")
            return 0

        run_training(settings)

    except RailScanError as exc:
        print(f"YOLO training failed: {exc}", file=sys.stderr)
        return 1

    print("YOLO training completed successfully.")
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
        raise ConfigError(f"Training value {key!r} must be an integer.") from exc

    if parsed <= 0:
        raise ConfigError(f"Training value {key!r} must be greater than zero.")

    return parsed


def _dataset_root(data_yaml: Path, dataset_config: Mapping[str, Any]) -> Path:
    raw_path = dataset_config.get("path", ".")
    root = Path(str(raw_path))
    if root.is_absolute():
        return root
    return (data_yaml.parent / root).resolve()


def _validate_dataset_paths(dataset_config: Mapping[str, Any]) -> None:
    for key in DATASET_SPLITS:
        value = dataset_config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"Dataset YAML must define a non-empty {key!r} path.")


def _config_class_names(config: Mapping[str, Any]) -> tuple[str, ...]:
    model_config = config.get("model", {})
    if not isinstance(model_config, Mapping):
        return ()
    return _read_class_names(
        model_config.get("class_names", model_config.get("danger_classes", ()))
    )


def _read_class_names(raw_names: Any) -> tuple[str, ...]:
    if isinstance(raw_names, Mapping):
        try:
            items = sorted(raw_names.items(), key=lambda item: int(item[0]))
        except (TypeError, ValueError) as exc:
            raise ConfigError("Dataset class name keys must be numeric.") from exc
        return tuple(str(name).strip() for _, name in items if str(name).strip())
    if isinstance(raw_names, list):
        return tuple(str(name).strip() for name in raw_names if str(name).strip())
    return ()


if __name__ == "__main__":
    raise SystemExit(main())
