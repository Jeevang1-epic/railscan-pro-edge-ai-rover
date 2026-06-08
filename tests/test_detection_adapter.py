import numpy as np
import pytest

from railscan.decision import Detection
from railscan.detection_adapter import (
    DetectionAdapterConfig,
    ParsedCandidate,
    YoloDetectionAdapter,
    bbox_iou,
    cxcywh_to_xyxy,
    non_max_suppression,
)
from railscan.exceptions import DetectionAdapterError


def make_config(**overrides) -> DetectionAdapterConfig:
    values = {
        "class_names": ("visible_crack", "surface_damage", "foreign_object"),
        "confidence_threshold": 0.50,
        "iou_threshold": 0.45,
        "input_box_format": "cxcywh",
        "has_objectness": False,
        "max_detections": 100,
    }
    values.update(overrides)
    return DetectionAdapterConfig(**values)


def make_rows() -> np.ndarray:
    return np.array(
        [
            [100.0, 100.0, 20.0, 20.0, 0.90, 0.10, 0.05],
            [200.0, 200.0, 40.0, 20.0, 0.20, 0.85, 0.05],
            [300.0, 300.0, 10.0, 10.0, 0.20, 0.10, 0.20],
        ],
        dtype=np.float32,
    )


def test_nhw_output_parses() -> None:
    adapter = YoloDetectionAdapter(make_config())

    detections = adapter.parse((make_rows()[np.newaxis, :, :],))

    assert len(detections) == 2
    assert detections[0].class_name == "visible_crack"
    assert detections[0].confidence == pytest.approx(0.90)
    assert detections[0].bbox == (90.0, 90.0, 110.0, 110.0)


def test_nchw_like_output_parses() -> None:
    adapter = YoloDetectionAdapter(make_config())
    output = make_rows().T[np.newaxis, :, :]

    detections = adapter.parse((output,))

    assert len(detections) == 2
    assert detections[1].class_name == "surface_damage"


def test_two_dimensional_output_parses() -> None:
    adapter = YoloDetectionAdapter(make_config())

    detections = adapter.parse((make_rows(),))

    assert len(detections) == 2


def test_objectness_layout_parses() -> None:
    adapter = YoloDetectionAdapter(make_config(has_objectness=True))
    rows = np.array(
        [
            [100.0, 100.0, 20.0, 20.0, 0.80, 0.90, 0.10, 0.05],
            [200.0, 200.0, 20.0, 20.0, 0.40, 0.90, 0.10, 0.05],
        ],
        dtype=np.float32,
    )

    detections = adapter.parse((rows,))

    assert len(detections) == 1
    assert detections[0].confidence == pytest.approx(0.72)


def test_low_confidence_candidates_are_filtered() -> None:
    adapter = YoloDetectionAdapter(make_config(confidence_threshold=0.95))

    detections = adapter.parse((make_rows(),))

    assert detections == ()


def test_class_names_are_mapped_correctly() -> None:
    adapter = YoloDetectionAdapter(make_config())

    detections = adapter.parse((make_rows(),))

    assert [detection.class_name for detection in detections] == [
        "visible_crack",
        "surface_damage",
    ]


def test_bbox_conversion_works() -> None:
    assert cxcywh_to_xyxy(10.0, 20.0, 4.0, 6.0) == (8.0, 17.0, 12.0, 23.0)


def test_iou_calculation_works() -> None:
    iou = bbox_iou((0.0, 0.0, 10.0, 10.0), (5.0, 5.0, 15.0, 15.0))

    assert iou == pytest.approx(25.0 / 175.0)


def test_nms_suppresses_overlapping_boxes_of_same_class() -> None:
    candidates = (
        ParsedCandidate(0, "visible_crack", 0.90, (0.0, 0.0, 10.0, 10.0)),
        ParsedCandidate(0, "visible_crack", 0.80, (1.0, 1.0, 11.0, 11.0)),
    )

    kept = non_max_suppression(
        candidates,
        iou_threshold=0.45,
        max_detections=10,
        class_aware=True,
    )

    assert kept == (candidates[0],)


def test_class_aware_nms_keeps_overlapping_boxes_of_different_classes() -> None:
    candidates = (
        ParsedCandidate(0, "visible_crack", 0.90, (0.0, 0.0, 10.0, 10.0)),
        ParsedCandidate(1, "surface_damage", 0.80, (1.0, 1.0, 11.0, 11.0)),
    )

    kept = non_max_suppression(
        candidates,
        iou_threshold=0.45,
        max_detections=10,
        class_aware=True,
    )

    assert kept == candidates


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"class_names": ()}, "class_names"),
        ({"confidence_threshold": -0.1}, "confidence_threshold"),
        ({"confidence_threshold": 1.1}, "confidence_threshold"),
        ({"iou_threshold": -0.1}, "iou_threshold"),
        ({"input_box_format": "xyxy"}, "input_box_format"),
        ({"has_objectness": "sometimes"}, "has_objectness"),
        ({"max_detections": 0}, "max_detections"),
    ],
)
def test_invalid_config_raises_clear_error(overrides: dict, message: str) -> None:
    with pytest.raises(DetectionAdapterError, match=message):
        make_config(**overrides)


def test_invalid_output_shape_raises_clear_error() -> None:
    adapter = YoloDetectionAdapter(make_config())

    with pytest.raises(DetectionAdapterError, match="shape"):
        adapter.parse((np.zeros((1, 2, 3, 4), dtype=np.float32),))


def test_wrong_column_count_raises_clear_error() -> None:
    adapter = YoloDetectionAdapter(make_config())

    with pytest.raises(DetectionAdapterError, match="columns|class count"):
        adapter.parse((np.zeros((2, 6), dtype=np.float32),))


def test_max_detections_cap_works() -> None:
    adapter = YoloDetectionAdapter(make_config(max_detections=1))

    detections = adapter.parse((make_rows(),))

    assert len(detections) == 1
    assert detections[0].class_name == "visible_crack"


def test_parsed_objects_are_existing_detection_instances() -> None:
    adapter = YoloDetectionAdapter(make_config())

    detections = adapter.parse((make_rows(),))

    assert all(isinstance(detection, Detection) for detection in detections)
