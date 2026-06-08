import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FINAL_DOCS = (
    "docs/final-qa-checklist.md",
    "docs/demo-runbook.md",
    "docs/hardware-validation-checklist.md",
    "docs/demo-script.md",
    "docs/demo-report-template.md",
)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_final_qa_docs_exist() -> None:
    for relative_path in FINAL_DOCS:
        assert (REPO_ROOT / relative_path).is_file()


def test_final_qa_script_exists_and_runs() -> None:
    assert (REPO_ROOT / "scripts" / "final_qa.py").is_file()

    result = run_script("scripts/final_qa.py")

    assert result.returncode == 0, result.stderr
    assert "Final QA checks passed." in result.stdout


def test_readme_contains_safe_demo_command() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert (
        "python scripts/run_demo.py --synthetic --mock-inference "
        "--serial-dry-run --frames 5"
    ) in readme


def test_docs_mention_real_stop_safety_flags() -> None:
    combined_docs = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "docs/runtime-integration.md", "docs/demo-runbook.md")
    )

    assert "--enable-real-stop" in combined_docs
    assert "--confirm-wheels-lifted" in combined_docs


def test_docs_do_not_claim_real_hardware_validation_passed() -> None:
    docs_text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (REPO_ROOT / "docs").glob("*.md")
    )

    forbidden_claims = (
        "real hardware validation passed",
        "real serial hardware validation passed",
        "real camera validation passed",
        "real arduino stop validation passed",
        "certified railway",
        "prevents all derailments",
        "official indian railways",
    )
    for claim in forbidden_claims:
        assert claim not in docs_text
