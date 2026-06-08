"""YAML configuration loading and validation."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from railscan.exceptions import ConfigError

REQUIRED_CONFIG_SECTIONS: tuple[str, ...] = (
    "camera",
    "serial",
    "model",
    "decision",
    "logging",
)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "railscan.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load and validate a RailScan YAML config file."""

    config_path = Path(path)

    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            raw_config = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Config file is not valid YAML: {config_path}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read config file: {config_path}") from exc

    if raw_config is None:
        raise ConfigError(f"Config file is empty: {config_path}")

    if not isinstance(raw_config, Mapping):
        raise ConfigError(f"Config root must be a mapping: {config_path}")

    config = dict(raw_config)
    validate_config(config, path=config_path)
    return config


def validate_config(config: Mapping[str, Any], *, path: str | Path | None = None) -> None:
    """Validate required top-level config sections."""

    missing_sections = [
        section for section in REQUIRED_CONFIG_SECTIONS if section not in config
    ]
    if missing_sections:
        location = f" in {Path(path)}" if path is not None else ""
        missing = ", ".join(missing_sections)
        required = ", ".join(REQUIRED_CONFIG_SECTIONS)
        raise ConfigError(
            f"Missing required config section(s){location}: {missing}. "
            f"Required sections: {required}."
        )

    invalid_sections = [
        section
        for section in REQUIRED_CONFIG_SECTIONS
        if not isinstance(config.get(section), Mapping)
    ]
    if invalid_sections:
        location = f" in {Path(path)}" if path is not None else ""
        invalid = ", ".join(invalid_sections)
        raise ConfigError(
            f"Config section(s){location} must be mappings: {invalid}."
        )
