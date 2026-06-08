import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SUBMISSION_DOCS = (
    "docs/release-notes-v0.1.0.md",
    "docs/submission-summary.md",
    "docs/judge-walkthrough.md",
    "docs/demo-video-shot-list.md",
    "docs/evidence-capture-checklist.md",
)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_submission_docs_exist() -> None:
    for relative_path in SUBMISSION_DOCS:
        assert (REPO_ROOT / relative_path).is_file()


def test_package_demo_artifacts_script_exists_and_runs() -> None:
    script = REPO_ROOT / "scripts" / "package_demo_artifacts.py"
    assert script.is_file()

    result = run_script("scripts/package_demo_artifacts.py")

    assert result.returncode == 0, result.stderr
    assert "Demo submission package written to:" in result.stdout


def test_package_manifest_is_created() -> None:
    result = run_script("scripts/package_demo_artifacts.py")
    assert result.returncode == 0, result.stderr

    manifest_path = REPO_ROOT / "dist" / "demo-submission" / "manifest.json"
    assert manifest_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.0"
    assert "validation_commands" in manifest
    assert "copied_docs" in manifest
    assert "runtime_report_path" in manifest


def test_manifest_excludes_large_model_and_dataset_artifacts() -> None:
    run_script("scripts/package_demo_artifacts.py")
    manifest_path = REPO_ROOT / "dist" / "demo-submission" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    copied_docs = "\n".join(manifest["copied_docs"])
    excluded_artifacts = "\n".join(manifest["excluded_artifacts"])

    assert ".onnx" not in copied_docs
    assert ".pt" not in copied_docs
    assert "datasets/railscan_v1/images/" in excluded_artifacts
    assert "datasets/railscan_v1/labels/" in excluded_artifacts
    assert "models/*.onnx" in excluded_artifacts


def test_release_notes_mention_safe_demo_and_limitations() -> None:
    text = (REPO_ROOT / "docs" / "release-notes-v0.1.0.md").read_text(encoding="utf-8").lower()

    assert "safe demo" in text
    assert "known limitations" in text
    assert "hardware" in text
    assert "pending" in text


def test_judge_walkthrough_mentions_safety_flags() -> None:
    text = (REPO_ROOT / "docs" / "judge-walkthrough.md").read_text(encoding="utf-8")

    assert "--enable-real-stop" in text
    assert "--confirm-wheels-lifted" in text
