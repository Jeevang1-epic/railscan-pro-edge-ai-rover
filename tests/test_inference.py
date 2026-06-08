from pathlib import Path

import numpy as np
import pytest

from railscan.config import load_config
from railscan.exceptions import InferenceError
from railscan.inference import (
    InferenceConfig,
    RailScanInferenceEngine,
    create_synthetic_frame,
)


def test_mock_inference_engine_loads() -> None:
    engine = RailScanInferenceEngine(
        InferenceConfig(model_path=Path("missing.onnx"), mock=True)
    )

    engine.load()

    assert engine.is_loaded is True
    engine.close()


def test_preprocessing_returns_expected_shape() -> None:
    config = InferenceConfig(model_path=Path("missing.onnx"), input_size=320, mock=True)
    frame = create_synthetic_frame(width=640, height=480)
    engine = RailScanInferenceEngine(config)

    tensor = engine.preprocess(frame)

    assert tensor.shape == (1, 3, 320, 320)
    assert tensor.dtype == np.float32
    assert 0.0 <= float(tensor.min()) <= float(tensor.max()) <= 1.0


def test_mock_run_returns_raw_outputs() -> None:
    config = InferenceConfig(model_path=Path("missing.onnx"), input_size=320, mock=True)
    frame = create_synthetic_frame(width=640, height=480)

    with RailScanInferenceEngine(config) as engine:
        result = engine.run(frame)

    assert result.raw_outputs
    assert result.input_shape == (1, 3, 320, 320)
    assert result.output_shapes == tuple(tuple(output.shape) for output in result.raw_outputs)


def test_mock_latency_is_non_negative() -> None:
    config = InferenceConfig(model_path=Path("missing.onnx"), mock=True)
    frame = create_synthetic_frame()

    result = RailScanInferenceEngine(config).run(frame)

    assert result.latency_ms >= 0.0


def test_invalid_frame_shape_raises_clear_error() -> None:
    engine = RailScanInferenceEngine(
        InferenceConfig(model_path=Path("missing.onnx"), mock=True)
    )
    invalid_frame = np.zeros((320, 320), dtype=np.uint8)

    with pytest.raises(InferenceError, match="HxWx3"):
        engine.preprocess(invalid_frame)


def test_missing_real_model_path_raises_clear_error() -> None:
    engine = RailScanInferenceEngine(
        InferenceConfig(model_path=Path("models/does_not_exist.onnx"), mock=False)
    )

    with pytest.raises(InferenceError, match="not found"):
        engine.load()


def test_inference_config_can_load_from_default_yaml() -> None:
    app_config = load_config(Path("config") / "railscan.yaml")
    config = InferenceConfig.from_mapping(app_config["model"], mock=True)

    assert config.model_path == Path("models/railscan_yolo.onnx")
    assert config.input_size == 320
    assert config.providers == ("CPUExecutionProvider",)
    assert config.mock is True


def test_inference_config_parses_string_boolean_values() -> None:
    config = InferenceConfig.from_mapping(
        {
            "path": "models/railscan_yolo.onnx",
            "input_size": 320,
            "confidence_threshold": 0.5,
            "providers": ["CPUExecutionProvider"],
            "mock": "false",
        }
    )

    assert config.mock is False
