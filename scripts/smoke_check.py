"""Smoke check for the Prompt 1 RailScan Pro foundation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import railscan  # noqa: E402


def main() -> int:
    config = railscan.load_config(REPO_ROOT / "config" / "railscan.yaml")
    logger = railscan.setup_logging(config)
    logger.info("RailScan Pro Prompt 1 smoke check completed.")
    print("RailScan Pro Prompt 1 smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
