"""Final no-hardware QA checks for RailScan Pro."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.exceptions import RailScanError  # noqa: E402

REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    "requirements-train.txt",
    "config/railscan.yaml",
    "src/railscan/runtime.py",
    "scripts/run_demo.py",
    "scripts/serial_stop_test.py",
    "scripts/camera_test.py",
    "scripts/inference_test.py",
    "scripts/detection_test.py",
    "scripts/decision_test.py",
    "scripts/train_yolo.py",
    "scripts/export_onnx.py",
    "scripts/validate_model_artifact.py",
    "docs/runtime-integration.md",
    "docs/model-training-export.md",
    "docs/detection-adapter.md",
    "docs/decision-engine.md",
    "docs/final-qa-checklist.md",
    "docs/demo-runbook.md",
    "docs/hardware-validation-checklist.md",
    "docs/demo-script.md",
    "docs/demo-report-template.md",
    "docs/release-notes-v0.1.0.md",
    "docs/submission-summary.md",
    "docs/judge-walkthrough.md",
    "docs/demo-video-shot-list.md",
    "docs/evidence-capture-checklist.md",
    "scripts/package_demo_artifacts.py",
)

RECOMMENDED_COMMANDS = (
    "python -m pip install -r requirements.txt",
    "python scripts/smoke_check.py",
    "python scripts/final_qa.py",
    "python scripts/package_demo_artifacts.py",
    "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5",
    "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3",
    "python scripts/validate_model_artifact.py --model models/railscan_yolo.onnx --allow-missing",
    "python scripts/detection_test.py",
    "python scripts/decision_test.py",
    "python scripts/serial_stop_test.py --dry-run",
    "python scripts/camera_test.py --synthetic --frames 5",
    "python scripts/inference_test.py --mock",
    "python scripts/benchmark_inference.py --mock --runs 5",
    "python scripts/train_yolo.py --dry-run",
    "python scripts/export_onnx.py --dry-run",
    "python -m pytest",
    "python -m compileall src scripts",
)


def main() -> int:
    failures: list[str] = []

    print("RailScan Pro final QA")
    print("Checking required files and safe-demo docs...")

    for relative_path in REQUIRED_FILES:
        path = REPO_ROOT / relative_path
        if not path.is_file():
            failures.append(f"missing required file: {relative_path}")

    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
    except RailScanError as exc:
        failures.append(f"config load failed: {exc}")
        config = {}

    runtime_config = config.get("runtime", {})
    output_dir = runtime_config.get("output_dir", "runs/reports")
    try:
        report_dir = REPO_ROOT / Path(str(output_dir))
        report_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        failures.append(f"cannot create runtime report directory: {exc}")

    if failures:
        print("Final QA failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Final QA checks passed.")
    print("Recommended validation commands:")
    for command in RECOMMENDED_COMMANDS:
        print(f"- {command}")
    print("Optional real camera/model/serial checks are documented but not run here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
