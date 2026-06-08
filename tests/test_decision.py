import pytest

from railscan.config import load_config
from railscan.decision import (
    DecisionConfig,
    Detection,
    RailScanDecisionEngine,
)
from railscan.exceptions import DecisionError


def make_config(**overrides) -> DecisionConfig:
    values = {
        "danger_classes": frozenset({"visible_crack", "foreign_object"}),
        "confidence_threshold": 0.50,
        "high_confidence_threshold": 0.80,
        "smoothing_enabled": True,
        "required_hits": 2,
        "window_size": 3,
    }
    values.update(overrides)
    return DecisionConfig(**values)


def test_valid_config_constructs_engine() -> None:
    config = DecisionConfig.from_app_config(load_config())
    engine = RailScanDecisionEngine(config)

    assert engine.latched is False
    assert "visible_crack" in config.danger_classes


def test_invalid_threshold_config_raises_clear_error() -> None:
    with pytest.raises(DecisionError, match="high_confidence_threshold"):
        make_config(confidence_threshold=0.90, high_confidence_threshold=0.80)


def test_non_danger_class_does_not_stop() -> None:
    engine = RailScanDecisionEngine(make_config())

    result = engine.update([Detection("background", 0.99)])

    assert result.should_stop is False
    assert result.matched_detections == ()


def test_low_confidence_danger_does_not_stop() -> None:
    engine = RailScanDecisionEngine(make_config())

    result = engine.update([Detection("visible_crack", 0.49)])

    assert result.should_stop is False
    assert result.matched_detections == ()


def test_threshold_equality_counts_as_valid_danger_hit() -> None:
    engine = RailScanDecisionEngine(make_config(required_hits=2, window_size=2))

    result = engine.update([Detection("visible_crack", 0.50)])

    assert result.should_stop is False
    assert result.matched_detections == (Detection("visible_crack", 0.50),)
    assert result.danger_hits_in_window == 1


def test_high_confidence_danger_triggers_immediately() -> None:
    engine = RailScanDecisionEngine(make_config())

    result = engine.update([Detection("visible_crack", 0.80)])

    assert result.should_stop is True
    assert result.latched is True
    assert result.trigger_type == "high_confidence"


def test_high_confidence_non_danger_class_does_not_stop() -> None:
    engine = RailScanDecisionEngine(make_config())

    result = engine.update([Detection("background", 1.0)])

    assert result.should_stop is False
    assert result.trigger_type == "none"
    assert result.matched_detections == ()


def test_smoothing_triggers_after_required_hits() -> None:
    engine = RailScanDecisionEngine(make_config())

    first = engine.update([Detection("visible_crack", 0.60)])
    second = engine.update([])
    third = engine.update([Detection("foreign_object", 0.60)])

    assert first.should_stop is False
    assert second.should_stop is False
    assert third.should_stop is True
    assert third.trigger_type == "smoothing"
    assert third.danger_hits_in_window == 2
    assert third.frames_in_window == 3


def test_low_confidence_and_non_danger_do_not_count_toward_smoothing() -> None:
    engine = RailScanDecisionEngine(make_config())

    first = engine.update([Detection("visible_crack", 0.49)])
    second = engine.update([Detection("background", 0.99)])
    third = engine.update([Detection("visible_crack", 0.60)])

    assert first.danger_hits_in_window == 0
    assert second.danger_hits_in_window == 0
    assert third.danger_hits_in_window == 1
    assert third.should_stop is False


def test_mixed_detections_count_when_one_valid_danger_exists() -> None:
    engine = RailScanDecisionEngine(make_config(required_hits=1, window_size=3))

    result = engine.update(
        [
            Detection("background", 0.99),
            Detection("visible_crack", 0.60),
        ]
    )

    assert result.should_stop is True
    assert result.trigger_type == "smoothing"
    assert result.matched_detections == (Detection("visible_crack", 0.60),)


def test_smoothing_window_rollover_uses_recent_frames_only() -> None:
    engine = RailScanDecisionEngine(make_config(required_hits=2, window_size=3))

    first = engine.update([Detection("visible_crack", 0.60)])
    second = engine.update([])
    third = engine.update([])
    fourth = engine.update([Detection("foreign_object", 0.60)])

    assert first.danger_hits_in_window == 1
    assert second.danger_hits_in_window == 1
    assert third.danger_hits_in_window == 1
    assert fourth.danger_hits_in_window == 1
    assert fourth.frames_in_window == 3
    assert fourth.should_stop is False


def test_latch_persists_after_trigger() -> None:
    engine = RailScanDecisionEngine(make_config())

    triggered = engine.update([Detection("visible_crack", 0.95)])
    after_trigger = engine.update([])

    assert triggered.should_stop is True
    assert after_trigger.should_stop is True
    assert after_trigger.latched is True
    assert after_trigger.trigger_type == "latched"


def test_latch_persists_after_multiple_updates() -> None:
    engine = RailScanDecisionEngine(make_config())
    engine.update([Detection("visible_crack", 0.95)])

    first_latched = engine.update([])
    second_latched = engine.update([Detection("background", 1.0)])

    assert first_latched.should_stop is True
    assert second_latched.should_stop is True
    assert first_latched.trigger_type == "latched"
    assert second_latched.trigger_type == "latched"


def test_reset_clears_latch() -> None:
    engine = RailScanDecisionEngine(make_config())
    engine.update([Detection("visible_crack", 0.95)])

    engine.reset()
    result = engine.update([])

    assert engine.latched is False
    assert result.should_stop is False
    assert result.frames_in_window == 1


def test_reset_clears_smoothing_history() -> None:
    engine = RailScanDecisionEngine(make_config())
    engine.update([Detection("visible_crack", 0.60)])

    engine.reset()
    result = engine.update([Detection("foreign_object", 0.60)])

    assert result.should_stop is False
    assert result.danger_hits_in_window == 1
    assert result.frames_in_window == 1


def test_required_hits_cannot_exceed_window_size() -> None:
    with pytest.raises(DecisionError, match="required_hits"):
        make_config(required_hits=4, window_size=3)


def test_empty_danger_classes_rejected() -> None:
    with pytest.raises(DecisionError, match="danger_classes"):
        make_config(danger_classes=frozenset())


def test_invalid_detection_confidence_raises_clear_error() -> None:
    with pytest.raises(DecisionError, match="confidence"):
        Detection("visible_crack", "not-a-number")


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_detection_confidence_out_of_range_raises_clear_error(confidence: float) -> None:
    with pytest.raises(DecisionError, match="between 0 and 1"):
        Detection("visible_crack", confidence)


def test_string_danger_class_is_treated_as_one_class() -> None:
    config = make_config(danger_classes="visible_crack")

    assert config.danger_classes == frozenset({"visible_crack"})


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"confidence_threshold": -0.1}, "confidence_threshold"),
        ({"confidence_threshold": 1.1}, "confidence_threshold"),
        ({"high_confidence_threshold": -0.1}, "high_confidence_threshold"),
        ({"required_hits": 0}, "required_hits"),
        ({"window_size": 0}, "window_size"),
        ({"smoothing_enabled": "sometimes"}, "smoothing_enabled"),
    ],
)
def test_invalid_config_cases_raise_decision_error(
    overrides: dict,
    message: str,
) -> None:
    with pytest.raises(DecisionError, match=message):
        make_config(**overrides)


def test_update_rejects_non_detection_inputs() -> None:
    engine = RailScanDecisionEngine(make_config())

    with pytest.raises(DecisionError, match="Detection"):
        engine.update([{"class_name": "visible_crack", "confidence": 0.9}])  # type: ignore[list-item]


def test_result_reason_and_trigger_type_values_are_stable() -> None:
    engine = RailScanDecisionEngine(make_config())

    result = engine.update([])

    assert result.reason == "no qualifying danger detections"
    assert result.trigger_type == "none"
