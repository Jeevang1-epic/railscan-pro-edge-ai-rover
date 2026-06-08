import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml

from railscan.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CLASSES = [
    "visible_crack",
    "surface_damage",
    "missing_fastener",
    "foreign_object",
    "unsafe_track_region",
]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_dataset_yaml_exists_and_has_expected_class_names() -> None:
    dataset_yaml = REPO_ROOT / "datasets" / "railscan_v1" / "data.yaml"

    data = yaml.safe_load(dataset_yaml.read_text(encoding="utf-8"))

    assert dataset_yaml.exists()
    assert data["train"] == "images/train"
    assert data["val"] == "images/val"
    assert data["test"] == "images/test"
    assert data["nc"] == len(EXPECTED_CLASSES)
    assert list(data["names"].values()) == EXPECTED_CLASSES


def test_training_dependencies_are_isolated() -> None:
    base_requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    train_requirements = (REPO_ROOT / "requirements-train.txt").read_text(
        encoding="utf-8"
    )

    for package in ("ultralytics", "torch", "onnx", "onnxsim"):
        assert package in train_requirements

    for package in ("ultralytics", "torch", "onnxsim"):
        assert package not in base_requirements


def test_train_dry_run_succeeds_without_dataset_images() -> None:
    result = run_script("scripts/train_yolo.py", "--dry-run")

    assert result.returncode == 0, result.stderr
    assert "Dry run: YOLO training was not started." in result.stdout


def test_export_dry_run_succeeds_without_weights() -> None:
    result = run_script("scripts/export_onnx.py", "--dry-run")

    assert result.returncode == 0, result.stderr
    assert "Dry run: ONNX export was not started." in result.stdout


def test_validate_artifact_allows_missing_model() -> None:
    result = run_script(
        "scripts/validate_model_artifact.py",
        "--model",
        "models/railscan_yolo.onnx",
        "--allow-missing",
    )

    assert result.returncode == 0, result.stderr
    assert "missing but allowed" in result.stdout


def test_validate_artifact_rejects_non_onnx_suffix() -> None:
    result = run_script(
        "scripts/validate_model_artifact.py",
        "--model",
        "models/railscan_yolo.pt",
        "--allow-missing",
    )

    assert result.returncode == 1
    assert "must use .onnx suffix" in result.stderr


def test_config_defaults_are_consistent() -> None:
    config = load_config()
    dataset_yaml = yaml.safe_load(
        (REPO_ROOT / "datasets" / "railscan_v1" / "data.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert config["training"]["data"] == "datasets/railscan_v1/data.yaml"
    assert config["training"]["base_model"] == "yolo11n.pt"
    assert config["training"]["imgsz"] == config["model"]["input_size"]
    assert config["export"]["weights"] == "runs/train/railscan_yolo/weights/best.pt"
    assert config["export"]["output"] == config["model"]["path"]
    assert config["export"]["format"] == "onnx"
    assert list(dataset_yaml["names"].values()) == config["model"]["class_names"]


def test_training_scripts_do_not_import_heavy_dependencies_at_module_import() -> None:
    for module_name in ("ultralytics", "torch"):
        sys.modules.pop(module_name, None)

    for script_name in ("train_yolo.py", "export_onnx.py"):
        script_path = REPO_ROOT / "scripts" / script_name
        module_name = f"railscan_prompt7_{script_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        sys.modules.pop(module_name, None)

    assert "ultralytics" not in sys.modules
    assert "torch" not in sys.modules
