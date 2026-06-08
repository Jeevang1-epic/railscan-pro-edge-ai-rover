"""Create a no-hardware demo submission package manifest."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist" / "demo-submission"
DOCS_DIR = DIST_DIR / "docs"

DOCS_TO_COPY = (
    "README.md",
    "docs/release-notes-v0.1.0.md",
    "docs/submission-summary.md",
    "docs/judge-walkthrough.md",
    "docs/demo-runbook.md",
    "docs/demo-video-shot-list.md",
    "docs/evidence-capture-checklist.md",
    "docs/final-qa-checklist.md",
    "docs/demo-report-template.md",
    "docs/hardware-validation-checklist.md",
    "docs/runtime-integration.md",
)

VALIDATION_COMMANDS = (
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

EXCLUDED_ARTIFACTS = (
    "models/*.onnx",
    "models/*.pt",
    "models/*.pth",
    "models/*.engine",
    "datasets/railscan_v1/images/",
    "datasets/railscan_v1/labels/",
    "runs/",
    ".pytest_cache/",
    "__pycache__/",
)


def git_commit_hash() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def copy_review_docs() -> list[str]:
    copied: list[str] = []
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    for relative_path in DOCS_TO_COPY:
        source = REPO_ROOT / relative_path
        if not source.is_file():
            continue

        destination = DOCS_DIR / source.name
        shutil.copy2(source, destination)
        copied.append(str(destination.relative_to(REPO_ROOT)).replace("\\", "/"))

    return copied


def find_runtime_report() -> str | None:
    report_path = REPO_ROOT / "runs" / "reports" / "runtime_summary.json"
    if report_path.is_file():
        return str(report_path.relative_to(REPO_ROOT)).replace("\\", "/")
    return None


def build_manifest(copied_docs: list[str]) -> dict[str, object]:
    return {
        "package": "RailScan Pro demo submission",
        "version": "0.1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit_hash(),
        "scope": "safe software demo packaging only",
        "safe_demo_commands": [
            "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5",
            "python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3",
        ],
        "validation_commands": list(VALIDATION_COMMANDS),
        "copied_docs": copied_docs,
        "runtime_report_path": find_runtime_report(),
        "excluded_artifacts": list(EXCLUDED_ARTIFACTS),
        "hardware_model_validation_status": {
            "real_camera": "not run by packaging script",
            "real_onnx_model": "not run by packaging script",
            "real_serial_stop": "not run by packaging script",
            "real_training_export": "not run by packaging script",
        },
        "safety_notes": [
            "Packaging does not open camera hardware.",
            "Packaging does not open serial ports.",
            "Packaging does not send STOP.",
            "Packaging does not train or export models.",
            "Real STOP remains gated by --enable-real-stop and --confirm-wheels-lifted.",
        ],
    }


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    copied_docs = copy_review_docs()
    manifest = build_manifest(copied_docs)

    manifest_path = DIST_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Demo submission package written to:")
    print(str(DIST_DIR.relative_to(REPO_ROOT)).replace("\\", "/"))
    print(f"Manifest: {manifest_path.relative_to(REPO_ROOT)}")
    print(f"Copied docs: {len(copied_docs)}")
    print("No hardware, camera, serial port, ONNX model, GPU, training, export, or STOP action was used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
