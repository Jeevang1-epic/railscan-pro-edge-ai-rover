from pathlib import Path

import pytest

from railscan.camera import CameraConfig, RailScanCamera
from railscan.config import load_config
from railscan.exceptions import CameraError


def test_synthetic_camera_opens() -> None:
    camera = RailScanCamera(CameraConfig(synthetic=True))

    camera.open()

    assert camera.is_open is True
    camera.close()


def test_synthetic_frame_has_expected_shape() -> None:
    config = CameraConfig(width=320, height=240, synthetic=True)

    with RailScanCamera(config) as camera:
        result = camera.read()

    assert result.frame.shape == (240, 320, 3)
    assert result.frame.dtype.name == "uint8"


def test_synthetic_frame_index_increments() -> None:
    with RailScanCamera(CameraConfig(synthetic=True)) as camera:
        first = camera.read()
        second = camera.read()

    assert first.frame_index == 1
    assert second.frame_index == 2
    assert second.fps is None or second.fps > 0


def test_camera_close_is_safe() -> None:
    camera = RailScanCamera(CameraConfig(synthetic=True))

    camera.close()
    camera.open()
    camera.close()
    camera.close()

    assert camera.is_open is False


def test_invalid_camera_config_raises_clear_error() -> None:
    with pytest.raises(CameraError, match="width"):
        CameraConfig.from_mapping(
            {
                "source": 0,
                "width": 0,
                "height": 480,
                "model_input_size": 320,
            }
        )


def test_camera_config_can_load_from_default_yaml() -> None:
    app_config = load_config(Path("config") / "railscan.yaml")
    camera_config = CameraConfig.from_mapping(app_config["camera"], synthetic=True)

    assert camera_config.source == 0
    assert camera_config.width == 640
    assert camera_config.height == 480
    assert camera_config.model_input_size == 320
    assert camera_config.synthetic is True


def test_camera_config_parses_string_boolean_values() -> None:
    camera_config = CameraConfig.from_mapping(
        {
            "source": 0,
            "width": 640,
            "height": 480,
            "model_input_size": 320,
            "synthetic": "false",
        }
    )

    assert camera_config.synthetic is False
