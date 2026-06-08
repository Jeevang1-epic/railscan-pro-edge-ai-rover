import json
import subprocess
import sys
from pathlib import Path

import pytest

from railscan.config import load_config
from railscan.exceptions import RuntimePipelineError
from railscan.runtime import RailScanRuntime, RuntimeConfig

REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeSerialConnection:
    is_open = True

    def __init__(self, *args, **kwargs) -> None:
        self.writes: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        self.is_open = False

    def readline(self) -> bytes:
        return b"EMERGENCY_STOP_LATCHED\n"


def make_runtime_config(tmp_path: Path, **overrides) -> RuntimeConfig:
    values = {
        "frames": 3,
        "synthetic": True,
        "mock_inference": True,
        "serial_dry_run": True,
        "enable_real_stop": False,
        "confirm_wheels_lifted": False,
        "simulate_defect_frame": None,
        "output_dir": tmp_path,
        "camera_source": 0,
        "model_path": Path("models/railscan_yolo.onnx"),
        "serial_port": "COM3",
    }
    values.update(overrides)
    return RuntimeConfig(**values)


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_default_runtime_config_is_safe() -> None:
    config = RuntimeConfig()

    assert config.synthetic is True
    assert config.mock_inference is True
    assert config.serial_dry_run is True
    assert config.real_stop_allowed is False
    assert config.frames == 10


def test_runtime_processes_finite_frames_and_writes_report(tmp_path: Path) -> None:
    app_config = load_config()
    runtime = RailScanRuntime(make_runtime_config(tmp_path, frames=2), app_config)

    summary = runtime.run()

    assert summary.frames_processed == 2
    assert summary.total_detections == 0
    assert summary.stop_action_mode == "none"
    assert summary.report_path == tmp_path / "runtime_summary.json"
    assert summary.report_path.exists()

    report = json.loads(summary.report_path.read_text(encoding="utf-8"))
    assert report["frames_processed"] == 2
    assert report["total_detections"] == 0
    assert report["decision_latched"] is False
    assert report["stop_action_mode"] == "none"
    assert report["stop_would_send"] is False
    assert report["stop_actually_sent"] is False
    assert Path(report["report_path"]).is_absolute() is False
    assert report["runtime_mode"]["synthetic"] is True
    assert report["runtime_mode"]["mock_inference"] is True
    assert "safety_flags" in report
    assert "latency_summary_ms" in report


def test_simulated_defect_triggers_decision_latch_and_dry_run_stop(
    tmp_path: Path,
) -> None:
    app_config = load_config()
    runtime = RailScanRuntime(
        make_runtime_config(tmp_path, frames=4, simulate_defect_frame=2),
        app_config,
    )

    summary = runtime.run()

    assert summary.decision_latched is True
    assert summary.stop_would_send is True
    assert summary.stop_actually_sent is False
    assert summary.stop_action_mode == "dry-run"
    assert summary.total_detections == 1
    assert summary.frame_results[1].simulated is True
    assert summary.frame_results[1].decision_should_stop is True


def test_real_stop_is_blocked_without_both_safety_flags(tmp_path: Path) -> None:
    app_config = load_config()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("serial factory should not be called")

    runtime = RailScanRuntime(
        make_runtime_config(
            tmp_path,
            frames=2,
            serial_dry_run=False,
            enable_real_stop=True,
            confirm_wheels_lifted=False,
            simulate_defect_frame=1,
        ),
        app_config,
        serial_factory=fail_if_called,
    )

    summary = runtime.run()

    assert summary.stop_action_mode == "blocked"
    assert summary.stop_would_send is True
    assert summary.stop_actually_sent is False


def test_real_stop_is_blocked_with_only_confirm_flag(tmp_path: Path) -> None:
    app_config = load_config()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("serial factory should not be called")

    runtime = RailScanRuntime(
        make_runtime_config(
            tmp_path,
            frames=2,
            serial_dry_run=False,
            enable_real_stop=False,
            confirm_wheels_lifted=True,
            simulate_defect_frame=1,
        ),
        app_config,
        serial_factory=fail_if_called,
    )

    summary = runtime.run()

    assert summary.stop_action_mode == "blocked"
    assert summary.stop_actually_sent is False


def test_cli_single_real_stop_flag_is_blocked() -> None:
    result = run_script(
        "scripts/run_demo.py",
        "--synthetic",
        "--mock-inference",
        "--frames",
        "2",
        "--simulate-defect-frame",
        "1",
        "--enable-real-stop",
    )

    assert result.returncode == 0, result.stderr
    assert "STOP action status: blocked" in result.stdout
    assert "STOP actually sent: False" in result.stdout


def test_real_stop_uses_fake_serial_only_when_both_flags_are_present(
    tmp_path: Path,
) -> None:
    app_config = load_config()
    connections: list[FakeSerialConnection] = []

    def fake_serial_factory(*args, **kwargs) -> FakeSerialConnection:
        connection = FakeSerialConnection()
        connections.append(connection)
        return connection

    runtime = RailScanRuntime(
        make_runtime_config(
            tmp_path,
            frames=2,
            serial_dry_run=False,
            enable_real_stop=True,
            confirm_wheels_lifted=True,
            simulate_defect_frame=1,
        ),
        app_config,
        serial_factory=fake_serial_factory,
    )

    summary = runtime.run()

    assert summary.stop_action_mode == "sent"
    assert summary.stop_actually_sent is True
    assert len(connections) == 1
    assert connections[0].writes == [b"S"]


def test_invalid_frame_count_fails_clearly(tmp_path: Path) -> None:
    with pytest.raises(RuntimePipelineError, match="frames"):
        make_runtime_config(tmp_path, frames=0)


def test_simulated_defect_frame_outside_range_fails_clearly(tmp_path: Path) -> None:
    with pytest.raises(RuntimePipelineError, match="simulate_defect_frame"):
        make_runtime_config(tmp_path, frames=3, simulate_defect_frame=4)


def test_report_parent_directory_is_created(tmp_path: Path) -> None:
    app_config = load_config()
    output_dir = tmp_path / "nested" / "reports"
    runtime = RailScanRuntime(make_runtime_config(output_dir, frames=1), app_config)

    summary = runtime.run()

    assert output_dir.exists()
    assert summary.report_path == output_dir / "runtime_summary.json"
