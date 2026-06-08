"""Safe runtime integration for RailScan Pro."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from railscan.camera import CameraConfig, RailScanCamera
from railscan.decision import DecisionConfig, DecisionResult, RailScanDecisionEngine
from railscan.detection_adapter import DetectionAdapterConfig, YoloDetectionAdapter
from railscan.exceptions import RuntimePipelineError
from railscan.inference import InferenceConfig, RailScanInferenceEngine
from railscan.serial_client import RailScanSerialClient, SerialConfig, SerialConnection

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration for the safe integrated runtime."""

    frames: int = 10
    synthetic: bool = True
    mock_inference: bool = True
    serial_dry_run: bool = True
    enable_real_stop: bool = False
    confirm_wheels_lifted: bool = False
    simulate_defect_frame: int | None = None
    output_dir: Path = Path("runs/reports")
    camera_source: int | str = 0
    model_path: Path = Path("models/railscan_yolo.onnx")
    serial_port: str = "COM3"

    def __post_init__(self) -> None:
        frames = _positive_int(self.frames, "frames")
        simulate_defect_frame = self.simulate_defect_frame
        if simulate_defect_frame is not None:
            simulate_defect_frame = _positive_int(
                simulate_defect_frame,
                "simulate_defect_frame",
            )
            if simulate_defect_frame > frames:
                raise RuntimePipelineError(
                    "simulate_defect_frame cannot be greater than frames."
                )

        object.__setattr__(self, "frames", frames)
        object.__setattr__(self, "synthetic", _coerce_bool(self.synthetic, "synthetic"))
        object.__setattr__(
            self,
            "mock_inference",
            _coerce_bool(self.mock_inference, "mock_inference"),
        )
        object.__setattr__(
            self,
            "serial_dry_run",
            _coerce_bool(self.serial_dry_run, "serial_dry_run"),
        )
        object.__setattr__(
            self,
            "enable_real_stop",
            _coerce_bool(self.enable_real_stop, "enable_real_stop"),
        )
        object.__setattr__(
            self,
            "confirm_wheels_lifted",
            _coerce_bool(self.confirm_wheels_lifted, "confirm_wheels_lifted"),
        )
        object.__setattr__(self, "simulate_defect_frame", simulate_defect_frame)
        object.__setattr__(self, "output_dir", Path(self.output_dir))
        object.__setattr__(self, "model_path", Path(self.model_path))
        object.__setattr__(self, "serial_port", str(self.serial_port).strip())

        if not str(self.serial_port).strip():
            raise RuntimePipelineError("serial_port cannot be empty.")

    @property
    def real_stop_allowed(self) -> bool:
        return self.enable_real_stop and self.confirm_wheels_lifted

    @classmethod
    def from_app_config(
        cls,
        config: Mapping[str, Any],
        *,
        frames: int | None = None,
        synthetic: bool | None = None,
        camera_source: int | str | None = None,
        mock_inference: bool | None = None,
        model_path: str | Path | None = None,
        serial_port: str | None = None,
        serial_dry_run: bool | None = None,
        enable_real_stop: bool | None = None,
        confirm_wheels_lifted: bool | None = None,
        simulate_defect_frame: int | None | object = ...,
        output_dir: str | Path | None = None,
    ) -> "RuntimeConfig":
        runtime_config = config.get("runtime", {})
        camera_config = config.get("camera", {})
        model_config = config.get("model", {})
        serial_config = config.get("serial", {})

        if not isinstance(runtime_config, Mapping):
            raise RuntimePipelineError("Loaded runtime config must be a mapping.")
        if not isinstance(camera_config, Mapping):
            raise RuntimePipelineError("Loaded camera config must be a mapping.")
        if not isinstance(model_config, Mapping):
            raise RuntimePipelineError("Loaded model config must be a mapping.")
        if not isinstance(serial_config, Mapping):
            raise RuntimePipelineError("Loaded serial config must be a mapping.")

        configured_simulation = runtime_config.get("simulate_defect_frame")
        if configured_simulation is None:
            configured_simulation = None

        return cls(
            frames=_read_int(runtime_config, "frames", 10) if frames is None else frames,
            synthetic=(
                _read_bool(runtime_config, "synthetic", True)
                if synthetic is None
                else synthetic
            ),
            mock_inference=(
                _read_bool(runtime_config, "mock_inference", True)
                if mock_inference is None
                else mock_inference
            ),
            serial_dry_run=(
                _read_bool(runtime_config, "serial_dry_run", True)
                if serial_dry_run is None
                else serial_dry_run
            ),
            enable_real_stop=(
                _read_bool(runtime_config, "enable_real_stop", False)
                if enable_real_stop is None
                else enable_real_stop
            ),
            confirm_wheels_lifted=(
                _read_bool(runtime_config, "confirm_wheels_lifted", False)
                if confirm_wheels_lifted is None
                else confirm_wheels_lifted
            ),
            simulate_defect_frame=(
                configured_simulation
                if simulate_defect_frame is ...
                else simulate_defect_frame
            ),
            output_dir=(
                runtime_config.get("output_dir", "runs/reports")
                if output_dir is None
                else output_dir
            ),
            camera_source=(
                camera_config.get("source", 0)
                if camera_source is None
                else camera_source
            ),
            model_path=model_config.get("path", "models/railscan_yolo.onnx")
            if model_path is None
            else model_path,
            serial_port=serial_config.get("port", "COM3")
            if serial_port is None
            else serial_port,
        )


@dataclass(frozen=True)
class StopActionResult:
    """Outcome of STOP handling for one frame."""

    mode: str
    would_send: bool
    actually_sent: bool
    dry_run: bool
    blocked_reason: str | None = None


@dataclass(frozen=True)
class RuntimeFrameResult:
    """Per-frame runtime result."""

    frame_index: int
    detection_count: int
    decision_should_stop: bool
    decision_latched: bool
    decision_reason: str
    stop_action: StopActionResult
    inference_latency_ms: float
    latency_ms: float
    simulated: bool


@dataclass(frozen=True)
class RuntimeSummary:
    """Summary of a finite safe runtime run."""

    frames_processed: int
    total_detections: int
    decision_latched: bool
    stop_would_send: bool
    stop_actually_sent: bool
    stop_action_mode: str
    runtime_mode: dict[str, Any]
    safety_flags: dict[str, bool]
    latency_summary_ms: dict[str, float]
    frame_results: tuple[RuntimeFrameResult, ...]
    report_path: Path | None


class RailScanRuntime:
    """Run the integrated RailScan pipeline in safe, finite modes."""

    def __init__(
        self,
        config: RuntimeConfig,
        app_config: Mapping[str, Any],
        *,
        serial_factory: Callable[..., SerialConnection] | None = None,
    ) -> None:
        self.config = config
        self.app_config = app_config
        self._serial_factory = serial_factory
        self._stop_client: RailScanSerialClient | None = None
        self._stop_handled = False

    def run(self, *, write_report: bool = True) -> RuntimeSummary:
        """Run the finite pipeline and return a structured summary."""

        camera = self._build_camera()
        inference_engine = self._build_inference_engine()
        adapter = YoloDetectionAdapter(DetectionAdapterConfig.from_app_config(self.app_config))
        decision_engine = RailScanDecisionEngine(
            DecisionConfig.from_app_config(self.app_config)
        )

        frame_results: list[RuntimeFrameResult] = []

        started = time.perf_counter()
        try:
            camera.open()
            inference_engine.load()

            for _ in range(self.config.frames):
                frame_started = time.perf_counter()
                frame_result = camera.read()
                inference_result = inference_engine.run(frame_result.frame)
                simulated = self._is_simulated_defect_frame(frame_result.frame_index)

                if self.config.mock_inference:
                    raw_outputs = self._mock_yolo_outputs(adapter.config, simulated)
                else:
                    raw_outputs = inference_result.raw_outputs

                detections = adapter.parse(raw_outputs)
                decision = decision_engine.update(detections)
                stop_action = self._handle_stop(decision)
                latency_ms = (time.perf_counter() - frame_started) * 1000.0

                frame_results.append(
                    RuntimeFrameResult(
                        frame_index=frame_result.frame_index,
                        detection_count=len(detections),
                        decision_should_stop=decision.should_stop,
                        decision_latched=decision.latched,
                        decision_reason=decision.reason,
                        stop_action=stop_action,
                        inference_latency_ms=inference_result.latency_ms,
                        latency_ms=latency_ms,
                        simulated=simulated,
                    )
                )
        finally:
            inference_engine.close()
            camera.close()
            if self._stop_client is not None:
                self._stop_client.close()

        summary = self._build_summary(frame_results)
        if write_report:
            report_path = self.write_report(summary)
            summary = RuntimeSummary(
                frames_processed=summary.frames_processed,
                total_detections=summary.total_detections,
                decision_latched=summary.decision_latched,
                stop_would_send=summary.stop_would_send,
                stop_actually_sent=summary.stop_actually_sent,
                stop_action_mode=summary.stop_action_mode,
                runtime_mode=summary.runtime_mode,
                safety_flags=summary.safety_flags,
                latency_summary_ms={
                    **summary.latency_summary_ms,
                    "total_runtime_ms": (time.perf_counter() - started) * 1000.0,
                },
                frame_results=summary.frame_results,
                report_path=report_path,
            )

        return summary

    def write_report(self, summary: RuntimeSummary) -> Path:
        """Write a JSON runtime summary and return its path."""

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.output_dir / "runtime_summary.json"
        report_path.write_text(
            json.dumps(_summary_to_dict(summary, report_path), indent=2),
            encoding="utf-8",
        )
        return report_path

    def _build_camera(self) -> RailScanCamera:
        camera_values = dict(self.app_config.get("camera", {}))
        camera_values["source"] = self.config.camera_source
        return RailScanCamera(
            CameraConfig.from_mapping(
                camera_values,
                synthetic=self.config.synthetic,
            )
        )

    def _build_inference_engine(self) -> RailScanInferenceEngine:
        model_values = dict(self.app_config.get("model", {}))
        return RailScanInferenceEngine(
            InferenceConfig.from_mapping(
                model_values,
                model_path=self.config.model_path,
                mock=self.config.mock_inference,
            )
        )

    def _build_stop_client(self) -> RailScanSerialClient:
        serial_values = dict(self.app_config.get("serial", {}))
        serial_values["port"] = self.config.serial_port
        return RailScanSerialClient(
            SerialConfig.from_mapping(
                serial_values,
                dry_run=self.config.serial_dry_run,
            ),
            serial_factory=self._serial_factory,
        )

    def _handle_stop(self, decision: DecisionResult) -> StopActionResult:
        if not decision.should_stop:
            return StopActionResult(
                mode="none",
                would_send=False,
                actually_sent=False,
                dry_run=self.config.serial_dry_run,
            )

        if self._stop_handled:
            return StopActionResult(
                mode="already-handled",
                would_send=False,
                actually_sent=False,
                dry_run=self.config.serial_dry_run,
            )

        if self.config.serial_dry_run:
            self._stop_client = self._stop_client or self._build_stop_client()
            self._stop_client.send_stop()
            self._stop_handled = True
            return StopActionResult(
                mode="dry-run",
                would_send=True,
                actually_sent=False,
                dry_run=True,
            )

        if not self.config.real_stop_allowed:
            self._stop_handled = True
            return StopActionResult(
                mode="blocked",
                would_send=True,
                actually_sent=False,
                dry_run=False,
                blocked_reason=(
                    "Real STOP requires --enable-real-stop and "
                    "--confirm-wheels-lifted."
                ),
            )

        self._stop_client = self._stop_client or self._build_stop_client()
        stop_result = self._stop_client.send_stop()
        self._stop_handled = True
        return StopActionResult(
            mode="sent",
            would_send=True,
            actually_sent=stop_result.sent and not stop_result.dry_run,
            dry_run=False,
        )

    def _is_simulated_defect_frame(self, frame_index: int) -> bool:
        return self.config.simulate_defect_frame == frame_index

    def _mock_yolo_outputs(
        self,
        adapter_config: DetectionAdapterConfig,
        simulated: bool,
    ) -> tuple[np.ndarray, ...]:
        score_offset = 5 if adapter_config.has_objectness else 4
        row = np.zeros((1, adapter_config.expected_columns), dtype=np.float32)
        row[0, :4] = (160.0, 160.0, 64.0, 48.0)

        if adapter_config.has_objectness:
            row[0, 4] = 1.0

        if simulated:
            score = min(max(adapter_config.confidence_threshold + 0.35, 0.85), 1.0)
        else:
            score = max(adapter_config.confidence_threshold - 0.10, 0.0)

        row[0, score_offset] = score
        return (row,)

    def _build_summary(
        self,
        frame_results: list[RuntimeFrameResult],
    ) -> RuntimeSummary:
        latencies = [result.latency_ms for result in frame_results]
        stop_modes = [
            result.stop_action.mode
            for result in frame_results
            if result.stop_action.mode != "none"
        ]
        stop_action_mode = stop_modes[-1] if stop_modes else "none"
        if "sent" in stop_modes:
            stop_action_mode = "sent"
        elif "dry-run" in stop_modes:
            stop_action_mode = "dry-run"
        elif "blocked" in stop_modes:
            stop_action_mode = "blocked"

        return RuntimeSummary(
            frames_processed=len(frame_results),
            total_detections=sum(result.detection_count for result in frame_results),
            decision_latched=any(result.decision_latched for result in frame_results),
            stop_would_send=any(
                result.stop_action.would_send for result in frame_results
            ),
            stop_actually_sent=any(
                result.stop_action.actually_sent for result in frame_results
            ),
            stop_action_mode=stop_action_mode,
            runtime_mode={
                "synthetic": self.config.synthetic,
                "mock_inference": self.config.mock_inference,
                "serial_dry_run": self.config.serial_dry_run,
                "simulate_defect_frame": self.config.simulate_defect_frame,
            },
            safety_flags={
                "enable_real_stop": self.config.enable_real_stop,
                "confirm_wheels_lifted": self.config.confirm_wheels_lifted,
                "real_stop_allowed": self.config.real_stop_allowed,
            },
            latency_summary_ms=_latency_summary(latencies),
            frame_results=tuple(frame_results),
            report_path=None,
        )


def _latency_summary(latencies: list[float]) -> dict[str, float]:
    if not latencies:
        return {
            "average": 0.0,
            "min": 0.0,
            "max": 0.0,
            "total_runtime_ms": 0.0,
        }

    return {
        "average": sum(latencies) / len(latencies),
        "min": min(latencies),
        "max": max(latencies),
        "total_runtime_ms": sum(latencies),
    }


def _summary_to_dict(
    summary: RuntimeSummary,
    report_path: Path | None = None,
) -> dict[str, Any]:
    data = asdict(summary)
    data["report_path"] = _report_path_string(report_path or summary.report_path)
    return data


def _report_path_string(path: Path | None) -> str | None:
    if path is None:
        return None

    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.name)


def _positive_int(value: Any, key: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimePipelineError(f"Runtime value {key!r} must be an integer.") from exc

    if parsed <= 0:
        raise RuntimePipelineError(f"Runtime value {key!r} must be greater than zero.")

    return parsed


def _coerce_bool(value: Any, key: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False

    raise RuntimePipelineError(f"Runtime value {key!r} must be a boolean.")


def _read_int(values: Mapping[str, Any], key: str, default: int) -> int:
    return _positive_int(values.get(key, default), key)


def _read_bool(values: Mapping[str, Any], key: str, default: bool) -> bool:
    return _coerce_bool(values.get(key, default), key)
