from pathlib import Path

import pytest

from railscan.config import REQUIRED_CONFIG_SECTIONS, load_config, validate_config
from railscan.exceptions import ConfigError


def test_default_config_loads() -> None:
    config = load_config(Path("config") / "railscan.yaml")

    assert set(REQUIRED_CONFIG_SECTIONS).issubset(config)
    assert config["serial"]["stop_command"] == "S"
    assert config["camera"]["model_input_size"] == 320


def test_required_config_sections_are_validated() -> None:
    incomplete_config = {
        "camera": {},
        "serial": {},
        "model": {},
        "decision": {},
    }

    with pytest.raises(ConfigError, match="logging"):
        validate_config(incomplete_config)


def test_required_config_sections_must_be_mappings() -> None:
    invalid_config = {
        "camera": {},
        "serial": {},
        "model": {},
        "decision": {},
        "logging": "runs/logs",
    }

    with pytest.raises(ConfigError, match="logging"):
        validate_config(invalid_config)
