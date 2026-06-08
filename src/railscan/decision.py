"""Pure decision logic for RailScan Pro."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from railscan.exceptions import DecisionError


@dataclass(frozen=True)
class Detection:
    """Normalized detection passed into the decision engine."""

    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float] | None = None

    def __post_init__(self) -> None:
        class_name = str(self.class_name).strip()
        if not class_name:
            raise DecisionError("Detection class_name cannot be empty.")

        confidence = _coerce_float(self.confidence, "confidence")
        if not 0.0 <= confidence <= 1.0:
            raise DecisionError("Detection confidence must be between 0 and 1.")

        object.__setattr__(self, "class_name", class_name)
        object.__setattr__(self, "confidence", confidence)

        if self.bbox is not None:
            try:
                bbox = tuple(float(value) for value in self.bbox)
            except (TypeError, ValueError) as exc:
                raise DecisionError("Detection bbox must contain numeric values.") from exc
            if len(bbox) != 4:
                raise DecisionError("Detection bbox must contain exactly four values.")
            object.__setattr__(self, "bbox", bbox)


@dataclass(frozen=True)
class DecisionConfig:
    """Thresholds and smoothing settings for stop decisions."""

    danger_classes: frozenset[str]
    confidence_threshold: float
    high_confidence_threshold: float
    smoothing_enabled: bool
    required_hits: int
    window_size: int

    def __post_init__(self) -> None:
        danger_classes = _normalize_danger_classes(self.danger_classes)
        confidence_threshold = _coerce_float(
            self.confidence_threshold,
            "confidence_threshold",
        )
        high_confidence_threshold = _coerce_float(
            self.high_confidence_threshold,
            "high_confidence_threshold",
        )
        smoothing_enabled = _coerce_bool(
            self.smoothing_enabled,
            "smoothing_enabled",
        )
        required_hits = _coerce_int(self.required_hits, "required_hits")
        window_size = _coerce_int(self.window_size, "window_size")

        if not 0.0 <= confidence_threshold <= 1.0:
            raise DecisionError("confidence_threshold must be between 0 and 1.")
        if not 0.0 <= high_confidence_threshold <= 1.0:
            raise DecisionError("high_confidence_threshold must be between 0 and 1.")
        if high_confidence_threshold < confidence_threshold:
            raise DecisionError(
                "high_confidence_threshold must be greater than or equal to "
                "confidence_threshold."
            )
        if required_hits < 1:
            raise DecisionError("required_hits must be at least 1.")
        if window_size < 1:
            raise DecisionError("window_size must be at least 1.")
        if required_hits > window_size:
            raise DecisionError("required_hits cannot exceed window_size.")

        object.__setattr__(self, "danger_classes", danger_classes)
        object.__setattr__(self, "confidence_threshold", confidence_threshold)
        object.__setattr__(self, "high_confidence_threshold", high_confidence_threshold)
        object.__setattr__(self, "smoothing_enabled", smoothing_enabled)
        object.__setattr__(self, "required_hits", required_hits)
        object.__setattr__(self, "window_size", window_size)

    @classmethod
    def from_app_config(cls, config: Mapping[str, Any]) -> "DecisionConfig":
        """Build decision config from the loaded RailScan config."""

        model_config = config.get("model")
        decision_config = config.get("decision")

        if not isinstance(model_config, Mapping):
            raise DecisionError("Loaded config must include a model mapping.")
        if not isinstance(decision_config, Mapping):
            raise DecisionError("Loaded config must include a decision mapping.")

        return cls.from_sections(model_config, decision_config)

    @classmethod
    def from_sections(
        cls,
        model_config: Mapping[str, Any],
        decision_config: Mapping[str, Any],
    ) -> "DecisionConfig":
        """Build decision config from model and decision config sections."""

        return cls(
            danger_classes=_normalize_danger_classes(
                model_config.get("danger_classes", ())
            ),
            confidence_threshold=_read_float(
                model_config,
                "confidence_threshold",
                0.50,
            ),
            high_confidence_threshold=_read_float(
                model_config,
                "high_confidence_threshold",
                0.80,
            ),
            smoothing_enabled=_read_bool(
                decision_config,
                "smoothing_enabled",
                True,
            ),
            required_hits=_read_int(decision_config, "required_hits", 2),
            window_size=_read_int(decision_config, "window_size", 3),
        )


@dataclass(frozen=True)
class DecisionResult:
    """Structured result for one decision update."""

    should_stop: bool
    latched: bool
    reason: str
    trigger_type: str
    matched_detections: tuple[Detection, ...]
    danger_hits_in_window: int
    frames_in_window: int


class RailScanDecisionEngine:
    """Stateful, latched decision engine with optional smoothing."""

    def __init__(self, config: DecisionConfig) -> None:
        self.config = config
        self._danger_window: deque[bool] = deque(maxlen=config.window_size)
        self._latched = False

    @property
    def latched(self) -> bool:
        return self._latched

    def update(self, detections: Sequence[Detection]) -> DecisionResult:
        """Update decision state from detections for a single frame."""

        normalized_detections = _normalize_detections(detections)

        if self._latched:
            return self._result(
                should_stop=True,
                reason="stop state is already latched",
                trigger_type="latched",
                matched_detections=(),
            )

        matched_detections = self._match_danger_detections(normalized_detections)
        frame_has_danger = bool(matched_detections)
        self._danger_window.append(frame_has_danger)

        high_confidence_matches = tuple(
            detection
            for detection in matched_detections
            if detection.confidence >= self.config.high_confidence_threshold
        )
        if high_confidence_matches:
            self._latched = True
            return self._result(
                should_stop=True,
                reason="high confidence danger detection",
                trigger_type="high_confidence",
                matched_detections=high_confidence_matches,
            )

        if self.config.smoothing_enabled and self._danger_hits() >= self.config.required_hits:
            self._latched = True
            return self._result(
                should_stop=True,
                reason="danger detections met temporal smoothing threshold",
                trigger_type="smoothing",
                matched_detections=matched_detections,
            )

        if matched_detections:
            reason = "danger detection below stop trigger threshold"
        else:
            reason = "no qualifying danger detections"

        return self._result(
            should_stop=False,
            reason=reason,
            trigger_type="none",
            matched_detections=matched_detections,
        )

    def reset(self) -> None:
        """Clear the latch and smoothing window."""

        self._latched = False
        self._danger_window.clear()

    def _match_danger_detections(
        self,
        detections: Sequence[Detection],
    ) -> tuple[Detection, ...]:
        return tuple(
            detection
            for detection in detections
            if detection.class_name in self.config.danger_classes
            and detection.confidence >= self.config.confidence_threshold
        )

    def _danger_hits(self) -> int:
        return sum(1 for has_danger in self._danger_window if has_danger)

    def _result(
        self,
        *,
        should_stop: bool,
        reason: str,
        trigger_type: str,
        matched_detections: tuple[Detection, ...],
    ) -> DecisionResult:
        return DecisionResult(
            should_stop=should_stop,
            latched=self._latched,
            reason=reason,
            trigger_type=trigger_type,
            matched_detections=matched_detections,
            danger_hits_in_window=self._danger_hits(),
            frames_in_window=len(self._danger_window),
        )


def _normalize_danger_classes(raw_classes: Any) -> frozenset[str]:
    if isinstance(raw_classes, str):
        raw_classes = (raw_classes,)

    try:
        classes = frozenset(
            str(class_name).strip()
            for class_name in raw_classes
            if str(class_name).strip()
        )
    except TypeError as exc:
        raise DecisionError("danger_classes must be an iterable of class names.") from exc

    if not classes:
        raise DecisionError("danger_classes cannot be empty.")

    return classes


def _normalize_detections(detections: Sequence[Detection]) -> tuple[Detection, ...]:
    if isinstance(detections, (str, bytes)):
        raise DecisionError("detections must be a sequence of Detection objects.")

    try:
        normalized = tuple(detections)
    except TypeError as exc:
        raise DecisionError("detections must be a sequence of Detection objects.") from exc

    if not all(isinstance(detection, Detection) for detection in normalized):
        raise DecisionError("detections must contain only Detection objects.")

    return normalized


def _coerce_float(value: Any, key: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DecisionError(f"Decision value {key!r} must be a number.") from exc


def _coerce_int(value: Any, key: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise DecisionError(f"Decision value {key!r} must be an integer.") from exc


def _coerce_bool(value: Any, key: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False

    raise DecisionError(f"Decision value {key!r} must be a boolean.")


def _read_float(values: Mapping[str, Any], key: str, default: float) -> float:
    return _coerce_float(values.get(key, default), key)


def _read_int(values: Mapping[str, Any], key: str, default: int) -> int:
    return _coerce_int(values.get(key, default), key)


def _read_bool(values: Mapping[str, Any], key: str, default: bool) -> bool:
    value = values.get(key, default)

    return _coerce_bool(value, key)
