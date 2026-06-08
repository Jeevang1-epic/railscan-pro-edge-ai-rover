"""ONNX inference foundation for RailScan Pro."""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from railscan.exceptions import InferenceError

DEFAULT_PROVIDER = "CPUExecutionProvider"


@dataclass(frozen=True)
class InferenceConfig:
    """Configuration for raw ONNX model inference."""

    model_path: Path
    input_size: int = 320
    confidence_threshold: float = 0.50
    providers: tuple[str, ...] = (DEFAULT_PROVIDER,)
    mock: bool = False

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, Any],
        *,
        model_path: str | Path | None = None,
        input_size: int | None = None,
        mock: bool | None = None,
    ) -> "InferenceConfig":
        """Build inference config from the `model` section of railscan.yaml."""

        configured_path = model_path if model_path is not None else values.get("path")
        if configured_path is None:
            raise InferenceError("Model config is missing required key: path.")

        resolved_input_size = (
            input_size
            if input_size is not None
            else _read_positive_int(values, "input_size", 320)
        )
        configured_mock = _read_bool(values, "mock", False) if mock is None else mock

        return cls(
            model_path=Path(configured_path),
            input_size=resolved_input_size,
            confidence_threshold=_read_float(
                values,
                "confidence_threshold",
                0.50,
            ),
            providers=_read_providers(values.get("providers", (DEFAULT_PROVIDER,))),
            mock=configured_mock,
        )


@dataclass(frozen=True)
class InferenceResult:
    """Raw output arrays and timing metadata from one inference run."""

    raw_outputs: tuple[np.ndarray, ...]
    latency_ms: float
    input_shape: tuple[int, ...]
    output_shapes: tuple[tuple[int, ...], ...]


class RailScanInferenceEngine:
    """Load an ONNX model and run raw frame inference."""

    def __init__(self, config: InferenceConfig) -> None:
        self.config = config
        self._session: Any | None = None
        self._input_name: str | None = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> "RailScanInferenceEngine":
        """Load ONNX Runtime session, or initialize mock mode."""

        if self._loaded:
            return self

        if self.config.mock:
            self._input_name = "mock_input"
            self._loaded = True
            return self

        if not self.config.model_path.exists():
            raise InferenceError(f"ONNX model not found: {self.config.model_path}")
        if not self.config.model_path.is_file():
            raise InferenceError(f"ONNX model path is not a file: {self.config.model_path}")

        ort = _load_onnxruntime()

        try:
            self._session = ort.InferenceSession(
                str(self.config.model_path),
                providers=list(self.config.providers),
            )
            inputs = self._session.get_inputs()
        except Exception as exc:
            raise InferenceError(f"Failed to load ONNX model: {self.config.model_path}") from exc

        if not inputs:
            raise InferenceError("ONNX model has no inputs.")

        self._input_name = inputs[0].name
        self._loaded = True
        return self

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Convert a BGR frame to a normalized BCHW float32 input tensor."""

        _validate_frame(frame)
        cv2 = _load_cv2()

        try:
            resized = cv2.resize(
                frame,
                (self.config.input_size, self.config.input_size),
                interpolation=cv2.INTER_LINEAR,
            )
            rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        except Exception as exc:
            raise InferenceError("Failed to preprocess inference frame.") from exc

        normalized = rgb_frame.astype(np.float32) / 255.0
        tensor = np.transpose(normalized, (2, 0, 1))[np.newaxis, ...]
        return np.ascontiguousarray(tensor, dtype=np.float32)

    def run(self, frame: np.ndarray) -> InferenceResult:
        """Preprocess a frame and run raw inference."""

        if not self._loaded:
            self.load()

        input_tensor = self.preprocess(frame)
        started = time.perf_counter()

        if self.config.mock:
            raw_outputs = self._run_mock(input_tensor)
        else:
            raw_outputs = self._run_onnx(input_tensor)

        latency_ms = (time.perf_counter() - started) * 1000.0
        return InferenceResult(
            raw_outputs=raw_outputs,
            latency_ms=latency_ms,
            input_shape=tuple(input_tensor.shape),
            output_shapes=tuple(tuple(output.shape) for output in raw_outputs),
        )

    def close(self) -> None:
        """Release runtime references. Safe to call multiple times."""

        self._session = None
        self._input_name = None
        self._loaded = False

    def _run_mock(self, input_tensor: np.ndarray) -> tuple[np.ndarray, ...]:
        mean_value = float(input_tensor.mean())
        output = np.array(
            [[[0.0, mean_value, self.config.confidence_threshold, 0.0, 0.0, 1.0]]],
            dtype=np.float32,
        )
        return (output,)

    def _run_onnx(self, input_tensor: np.ndarray) -> tuple[np.ndarray, ...]:
        if self._session is None or self._input_name is None:
            raise InferenceError("Inference session is not loaded.")

        try:
            outputs = self._session.run(None, {self._input_name: input_tensor})
        except Exception as exc:
            raise InferenceError("ONNX Runtime inference failed.") from exc

        return tuple(np.asarray(output) for output in outputs)

    def __enter__(self) -> "RailScanInferenceEngine":
        return self.load()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: Any,
    ) -> None:
        self.close()


def create_synthetic_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a deterministic BGR test frame for inference checks."""

    if width <= 0 or height <= 0:
        raise InferenceError("Synthetic frame width and height must be greater than zero.")

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :, 0] = 32
    frame[:, :, 1] = np.linspace(0, 255, width, dtype=np.uint8)
    frame[:, :, 2] = np.linspace(255, 0, height, dtype=np.uint8)[:, np.newaxis]
    return frame


def _validate_frame(frame: np.ndarray) -> None:
    if not isinstance(frame, np.ndarray):
        raise InferenceError("Inference frame must be a numpy array.")
    if frame.ndim != 3:
        raise InferenceError("Inference frame must have shape HxWx3.")
    if frame.shape[2] != 3:
        raise InferenceError("Inference frame must have exactly 3 channels.")
    if frame.shape[0] <= 0 or frame.shape[1] <= 0:
        raise InferenceError("Inference frame width and height must be greater than zero.")


def _read_positive_int(values: Mapping[str, Any], key: str, default: int) -> int:
    try:
        value = int(values.get(key, default))
    except (TypeError, ValueError) as exc:
        raise InferenceError(f"Model config value {key!r} must be an integer.") from exc

    if value <= 0:
        raise InferenceError(f"Model config value {key!r} must be greater than zero.")

    return value


def _read_float(values: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError) as exc:
        raise InferenceError(f"Model config value {key!r} must be a number.") from exc


def _read_bool(values: Mapping[str, Any], key: str, default: bool) -> bool:
    value = values.get(key, default)

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False

    raise InferenceError(f"Model config value {key!r} must be a boolean.")


def _read_providers(raw_providers: Any) -> tuple[str, ...]:
    if isinstance(raw_providers, str):
        providers = (raw_providers,)
    else:
        try:
            providers = tuple(str(provider) for provider in raw_providers)
        except TypeError as exc:
            raise InferenceError("Model providers must be a string or list of strings.") from exc

    if not providers or any(not provider.strip() for provider in providers):
        raise InferenceError("Model providers cannot be empty.")

    return tuple(provider.strip() for provider in providers)


def _load_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise InferenceError(
            "opencv-python is required for inference preprocessing. "
            "Install requirements.txt first."
        ) from exc

    return cv2


def _load_onnxruntime() -> Any:
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise InferenceError(
            "onnxruntime is required for real model inference. "
            "Install requirements.txt first."
        ) from exc

    return ort
