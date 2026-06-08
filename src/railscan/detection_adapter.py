"""YOLO-like output postprocessing for RailScan Pro."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from railscan.decision import Detection
from railscan.exceptions import DetectionAdapterError

SUPPORTED_BOX_FORMATS = frozenset({"cxcywh"})


@dataclass(frozen=True)
class DetectionAdapterConfig:
    """Configuration for converting raw model outputs into detections."""

    class_names: tuple[str, ...]
    confidence_threshold: float
    iou_threshold: float = 0.45
    input_box_format: str = "cxcywh"
    has_objectness: bool = False
    max_detections: int = 100

    def __post_init__(self) -> None:
        class_names = _normalize_class_names(self.class_names)
        confidence_threshold = _coerce_float(
            self.confidence_threshold,
            "confidence_threshold",
        )
        iou_threshold = _coerce_float(self.iou_threshold, "iou_threshold")
        input_box_format = str(self.input_box_format).strip().lower()
        has_objectness = _coerce_bool(self.has_objectness, "has_objectness")
        max_detections = _coerce_int(self.max_detections, "max_detections")

        if not 0.0 <= confidence_threshold <= 1.0:
            raise DetectionAdapterError(
                "confidence_threshold must be between 0 and 1."
            )
        if not 0.0 <= iou_threshold <= 1.0:
            raise DetectionAdapterError("iou_threshold must be between 0 and 1.")
        if input_box_format not in SUPPORTED_BOX_FORMATS:
            supported = ", ".join(sorted(SUPPORTED_BOX_FORMATS))
            raise DetectionAdapterError(
                f"input_box_format must be one of: {supported}."
            )
        if max_detections < 1:
            raise DetectionAdapterError("max_detections must be at least 1.")

        object.__setattr__(self, "class_names", class_names)
        object.__setattr__(self, "confidence_threshold", confidence_threshold)
        object.__setattr__(self, "iou_threshold", iou_threshold)
        object.__setattr__(self, "input_box_format", input_box_format)
        object.__setattr__(self, "has_objectness", has_objectness)
        object.__setattr__(self, "max_detections", max_detections)

    @property
    def expected_columns(self) -> int:
        score_offset = 5 if self.has_objectness else 4
        return score_offset + len(self.class_names)

    @classmethod
    def from_app_config(cls, config: Mapping[str, Any]) -> "DetectionAdapterConfig":
        """Build adapter config from the loaded RailScan config."""

        model_config = config.get("model")
        postprocessing_config = config.get("postprocessing", {})

        if not isinstance(model_config, Mapping):
            raise DetectionAdapterError("Loaded config must include a model mapping.")
        if not isinstance(postprocessing_config, Mapping):
            raise DetectionAdapterError("Loaded postprocessing config must be a mapping.")

        class_names = model_config.get(
            "class_names",
            model_config.get("danger_classes", ()),
        )

        return cls(
            class_names=_normalize_class_names(class_names),
            confidence_threshold=_read_float(
                model_config,
                "confidence_threshold",
                0.50,
            ),
            iou_threshold=_read_float(
                postprocessing_config,
                "iou_threshold",
                0.45,
            ),
            input_box_format=str(
                postprocessing_config.get("input_box_format", "cxcywh")
            ),
            has_objectness=_read_bool(
                postprocessing_config,
                "has_objectness",
                False,
            ),
            max_detections=_read_int(
                postprocessing_config,
                "max_detections",
                100,
            ),
        )


@dataclass(frozen=True)
class ParsedCandidate:
    """A parsed candidate before conversion to the decision Detection type."""

    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]


class YoloDetectionAdapter:
    """Convert YOLO-like raw outputs into normalized Detection objects."""

    def __init__(self, config: DetectionAdapterConfig) -> None:
        self.config = config

    def parse(self, raw_outputs: Sequence[np.ndarray]) -> tuple[Detection, ...]:
        """Parse raw output arrays and return normalized detections."""

        rows = self._normalize_outputs(raw_outputs)
        candidates = tuple(
            candidate
            for row in rows
            if (candidate := self._parse_row(row)) is not None
        )
        kept = non_max_suppression(
            candidates,
            iou_threshold=self.config.iou_threshold,
            max_detections=self.config.max_detections,
            class_aware=True,
        )

        return tuple(
            Detection(
                class_name=candidate.class_name,
                confidence=candidate.confidence,
                bbox=candidate.bbox,
            )
            for candidate in kept
        )

    def _normalize_outputs(self, raw_outputs: Sequence[np.ndarray]) -> np.ndarray:
        if isinstance(raw_outputs, np.ndarray):
            outputs = (raw_outputs,)
        else:
            try:
                outputs = tuple(raw_outputs)
            except TypeError as exc:
                raise DetectionAdapterError(
                    "raw_outputs must be a sequence of numpy arrays."
                ) from exc

        if not outputs:
            raise DetectionAdapterError("raw_outputs cannot be empty.")

        normalized_arrays = tuple(self._normalize_output_array(output) for output in outputs)
        if not normalized_arrays:
            raise DetectionAdapterError("raw_outputs did not contain any candidates.")

        return np.concatenate(normalized_arrays, axis=0)

    def _normalize_output_array(self, output: np.ndarray) -> np.ndarray:
        try:
            array = np.asarray(output, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            raise DetectionAdapterError(
                "raw output arrays must contain numeric values."
            ) from exc

        expected_columns = self.config.expected_columns

        if array.ndim == 2:
            rows = array
        elif array.ndim == 3 and array.shape[0] == 1:
            squeezed = array[0]
            if squeezed.ndim != 2:
                raise DetectionAdapterError("raw output shape is not supported.")
            if squeezed.shape[1] == expected_columns:
                rows = squeezed
            elif squeezed.shape[0] == expected_columns:
                rows = squeezed.T
            else:
                raise DetectionAdapterError(
                    "raw output shape does not match configured class count."
                )
        else:
            raise DetectionAdapterError(
                "raw output must have shape (1, N, 4+C), (1, 4+C, N), or (N, 4+C)."
            )

        if rows.ndim != 2 or rows.shape[1] != expected_columns:
            raise DetectionAdapterError(
                "raw output rows must contain exactly the configured box and score columns."
            )

        if rows.shape[0] == 0:
            raise DetectionAdapterError("raw output cannot contain zero candidates.")

        if not np.isfinite(rows).all():
            raise DetectionAdapterError("raw output contains non-finite values.")

        return np.ascontiguousarray(rows, dtype=np.float32)

    def _parse_row(self, row: np.ndarray) -> ParsedCandidate | None:
        score_offset = 5 if self.config.has_objectness else 4
        objectness = float(row[4]) if self.config.has_objectness else 1.0
        class_scores = row[score_offset:]

        if not 0.0 <= objectness <= 1.0:
            raise DetectionAdapterError("objectness score must be between 0 and 1.")

        if not np.all((0.0 <= class_scores) & (class_scores <= 1.0)):
            raise DetectionAdapterError("class scores must be between 0 and 1.")

        class_id = int(np.argmax(class_scores))
        class_confidence = float(class_scores[class_id])
        confidence = objectness * class_confidence

        if confidence < self.config.confidence_threshold:
            return None

        bbox = cxcywh_to_xyxy(row[0], row[1], row[2], row[3])
        return ParsedCandidate(
            class_id=class_id,
            class_name=self.config.class_names[class_id],
            confidence=confidence,
            bbox=bbox,
        )


def cxcywh_to_xyxy(
    cx: float,
    cy: float,
    width: float,
    height: float,
) -> tuple[float, float, float, float]:
    """Convert center-width-height box coordinates to xyxy coordinates."""

    cx_value = _coerce_float(cx, "cx")
    cy_value = _coerce_float(cy, "cy")
    width_value = _coerce_float(width, "width")
    height_value = _coerce_float(height, "height")

    if width_value < 0.0 or height_value < 0.0:
        raise DetectionAdapterError("bbox width and height cannot be negative.")

    half_width = width_value / 2.0
    half_height = height_value / 2.0
    return (
        cx_value - half_width,
        cy_value - half_height,
        cx_value + half_width,
        cy_value + half_height,
    )


def bbox_iou(
    bbox_a: Sequence[float],
    bbox_b: Sequence[float],
) -> float:
    """Calculate intersection-over-union for two xyxy boxes."""

    x1_a, y1_a, x2_a, y2_a = _normalize_bbox(bbox_a, "bbox_a")
    x1_b, y1_b, x2_b, y2_b = _normalize_bbox(bbox_b, "bbox_b")

    intersection_x1 = max(x1_a, x1_b)
    intersection_y1 = max(y1_a, y1_b)
    intersection_x2 = min(x2_a, x2_b)
    intersection_y2 = min(y2_a, y2_b)

    intersection_width = max(0.0, intersection_x2 - intersection_x1)
    intersection_height = max(0.0, intersection_y2 - intersection_y1)
    intersection_area = intersection_width * intersection_height

    area_a = (x2_a - x1_a) * (y2_a - y1_a)
    area_b = (x2_b - x1_b) * (y2_b - y1_b)
    union_area = area_a + area_b - intersection_area

    if union_area <= 0.0:
        return 0.0

    return intersection_area / union_area


def non_max_suppression(
    candidates: Sequence[ParsedCandidate],
    *,
    iou_threshold: float,
    max_detections: int,
    class_aware: bool = True,
) -> tuple[ParsedCandidate, ...]:
    """Apply deterministic NMS to parsed candidates."""

    iou_threshold = _coerce_float(iou_threshold, "iou_threshold")
    max_detections = _coerce_int(max_detections, "max_detections")

    if not 0.0 <= iou_threshold <= 1.0:
        raise DetectionAdapterError("iou_threshold must be between 0 and 1.")
    if max_detections < 1:
        raise DetectionAdapterError("max_detections must be at least 1.")

    indexed_candidates = tuple(enumerate(candidates))
    ordered = sorted(
        indexed_candidates,
        key=lambda item: (-item[1].confidence, item[0]),
    )

    kept: list[ParsedCandidate] = []
    for _, candidate in ordered:
        if len(kept) >= max_detections:
            break

        should_suppress = False
        for kept_candidate in kept:
            if class_aware and candidate.class_id != kept_candidate.class_id:
                continue
            if bbox_iou(candidate.bbox, kept_candidate.bbox) > iou_threshold:
                should_suppress = True
                break

        if not should_suppress:
            kept.append(candidate)

    return tuple(kept)


def _normalize_class_names(raw_class_names: Any) -> tuple[str, ...]:
    if isinstance(raw_class_names, str):
        raw_class_names = (raw_class_names,)

    try:
        class_names = tuple(
            str(class_name).strip()
            for class_name in raw_class_names
            if str(class_name).strip()
        )
    except TypeError as exc:
        raise DetectionAdapterError("class_names must be an iterable of names.") from exc

    if not class_names:
        raise DetectionAdapterError("class_names cannot be empty.")

    return class_names


def _normalize_bbox(
    bbox: Sequence[float],
    name: str,
) -> tuple[float, float, float, float]:
    try:
        values = tuple(float(value) for value in bbox)
    except (TypeError, ValueError) as exc:
        raise DetectionAdapterError(f"{name} must contain numeric values.") from exc

    if len(values) != 4:
        raise DetectionAdapterError(f"{name} must contain exactly four values.")

    x1, y1, x2, y2 = values
    if x2 < x1 or y2 < y1:
        raise DetectionAdapterError(f"{name} must use xyxy order with x2 >= x1 and y2 >= y1.")

    return x1, y1, x2, y2


def _coerce_float(value: Any, key: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise DetectionAdapterError(f"Detection adapter value {key!r} must be a number.") from exc


def _coerce_int(value: Any, key: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise DetectionAdapterError(
            f"Detection adapter value {key!r} must be an integer."
        ) from exc


def _coerce_bool(value: Any, key: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False

    raise DetectionAdapterError(
        f"Detection adapter value {key!r} must be a boolean."
    )


def _read_float(values: Mapping[str, Any], key: str, default: float) -> float:
    return _coerce_float(values.get(key, default), key)


def _read_int(values: Mapping[str, Any], key: str, default: int) -> int:
    return _coerce_int(values.get(key, default), key)


def _read_bool(values: Mapping[str, Any], key: str, default: bool) -> bool:
    return _coerce_bool(values.get(key, default), key)
