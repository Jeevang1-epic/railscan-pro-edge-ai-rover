"""Camera capture foundation for RailScan Pro."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from railscan.exceptions import CameraError


class VideoCapture(Protocol):
    """Small subset of cv2.VideoCapture used by RailScanCamera."""

    def isOpened(self) -> bool:
        ...

    def read(self) -> tuple[bool, np.ndarray | None]:
        ...

    def release(self) -> None:
        ...

    def set(self, prop_id: int, value: float) -> bool:
        ...


@dataclass(frozen=True)
class CameraConfig:
    """Configuration needed to open a camera source."""

    source: int | str = 0
    width: int = 640
    height: int = 480
    model_input_size: int = 320
    synthetic: bool = False

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, Any],
        *,
        synthetic: bool | None = None,
    ) -> "CameraConfig":
        """Build camera config from the `camera` section of railscan.yaml."""

        source = _normalize_source(values.get("source", 0))
        width = _read_positive_int(values, "width", 640)
        height = _read_positive_int(values, "height", 480)
        model_input_size = _read_positive_int(values, "model_input_size", 320)
        synthetic_mode = (
            _read_bool(values, "synthetic", False) if synthetic is None else synthetic
        )

        return cls(
            source=source,
            width=width,
            height=height,
            model_input_size=model_input_size,
            synthetic=synthetic_mode,
        )


@dataclass(frozen=True)
class FrameResult:
    """Frame plus lightweight metadata from one camera read."""

    frame: np.ndarray
    frame_index: int
    timestamp: float
    fps: float | None


class RailScanCamera:
    """Open, read, and close a camera source."""

    def __init__(
        self,
        config: CameraConfig,
        *,
        capture_factory: Callable[[int | str], VideoCapture] | None = None,
    ) -> None:
        self.config = config
        self._capture_factory = capture_factory
        self._capture: VideoCapture | None = None
        self._opened = False
        self._frame_index = 0
        self._start_time: float | None = None

    @property
    def is_open(self) -> bool:
        return self._opened

    def open(self) -> "RailScanCamera":
        """Open the configured source, or prepare synthetic frame generation."""

        if self._opened:
            return self

        self._frame_index = 0
        self._start_time = time.monotonic()

        if self.config.synthetic:
            self._opened = True
            return self

        cv2 = _load_cv2()
        factory = self._capture_factory or cv2.VideoCapture
        capture = factory(self.config.source)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.config.width))
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.config.height))

        if not capture.isOpened():
            capture.release()
            raise CameraError(f"Unable to open camera source: {self.config.source!r}")

        self._capture = capture
        self._opened = True
        return self

    def read(self) -> FrameResult:
        """Read one frame and return it with capture metadata."""

        if not self._opened:
            raise CameraError("Camera is not open.")

        if self.config.synthetic:
            frame = self._read_synthetic_frame()
        else:
            capture = self._require_capture()
            success, frame = capture.read()
            if not success or frame is None:
                raise CameraError("Failed to read frame from camera source.")

        self._frame_index += 1
        timestamp = time.time()
        return FrameResult(
            frame=frame,
            frame_index=self._frame_index,
            timestamp=timestamp,
            fps=self._calculate_fps(),
        )

    def close(self) -> None:
        """Release camera resources. Calling close more than once is safe."""

        if self._capture is not None:
            self._capture.release()
            self._capture = None

        self._opened = False

    def _read_synthetic_frame(self) -> np.ndarray:
        frame = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        marker = self._frame_index % max(self.config.width, 1)
        frame[:, marker : marker + 1, 1] = 255
        return frame

    def _calculate_fps(self) -> float | None:
        if self._start_time is None:
            return None

        elapsed = time.monotonic() - self._start_time
        if elapsed <= 0:
            return None

        return self._frame_index / elapsed

    def _require_capture(self) -> VideoCapture:
        if self._capture is None:
            raise CameraError("Camera capture is not initialized.")
        return self._capture

    def __enter__(self) -> "RailScanCamera":
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: Any,
    ) -> None:
        self.close()


def _normalize_source(source: Any) -> int | str:
    if isinstance(source, int):
        return source

    if isinstance(source, str):
        stripped = source.strip()
        if not stripped:
            raise CameraError("Camera source cannot be empty.")
        if stripped.isdigit():
            return int(stripped)
        return stripped

    raise CameraError("Camera source must be an integer index or path/URL string.")


def _read_positive_int(values: Mapping[str, Any], key: str, default: int) -> int:
    try:
        value = int(values.get(key, default))
    except (TypeError, ValueError) as exc:
        raise CameraError(f"Camera config value {key!r} must be an integer.") from exc

    if value <= 0:
        raise CameraError(f"Camera config value {key!r} must be greater than zero.")

    return value


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

    raise CameraError(f"Camera config value {key!r} must be a boolean.")


def _load_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise CameraError(
            "opencv-python is required for real camera mode. Install requirements.txt first."
        ) from exc

    return cv2
