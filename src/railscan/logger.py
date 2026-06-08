"""Logging setup for RailScan Pro."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(
    config: Mapping[str, Any] | None = None,
    *,
    logger_name: str = "railscan",
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure and return the package logger."""

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    output_dir = _get_logging_output_dir(config)
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(output_dir / "railscan.log", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _get_logging_output_dir(config: Mapping[str, Any] | None) -> Path | None:
    if config is None:
        return None

    logging_config = config.get("logging")
    if not isinstance(logging_config, Mapping):
        return None

    output_dir = logging_config.get("output_dir")
    if not isinstance(output_dir, str) or not output_dir.strip():
        return None

    return Path(output_dir)
