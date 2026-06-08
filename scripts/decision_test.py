"""CLI utility for validating RailScan Pro decision behavior."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.decision import (  # noqa: E402
    DecisionConfig,
    DecisionResult,
    Detection,
    RailScanDecisionEngine,
)
from railscan.exceptions import RailScanError  # noqa: E402


def print_result(label: str, result: DecisionResult) -> None:
    print(
        f"{label}: should_stop={result.should_stop}, "
        f"latched={result.latched}, trigger={result.trigger_type}, "
        f"hits={result.danger_hits_in_window}/{result.frames_in_window}, "
        f"reason={result.reason}"
    )


def main() -> int:
    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
        decision_config = DecisionConfig.from_app_config(config)
        danger_class = sorted(decision_config.danger_classes)[0]
        mid_confidence = (
            decision_config.confidence_threshold
            + decision_config.high_confidence_threshold
        ) / 2

        engine = RailScanDecisionEngine(decision_config)

        print_result("normal/no detections", engine.update([]))
        print_result(
            "non-danger detection",
            engine.update([Detection("background", 0.99)]),
        )
        print_result(
            "low-confidence danger",
            engine.update(
                [
                    Detection(
                        danger_class,
                        max(decision_config.confidence_threshold - 0.05, 0.0),
                    )
                ]
            ),
        )

        engine.reset()
        print_result(
            "high-confidence danger",
            engine.update([Detection(danger_class, decision_config.high_confidence_threshold)]),
        )
        print_result("latched after high confidence", engine.update([]))

        engine.reset()
        print_result(
            "smoothing frame 1",
            engine.update([Detection(danger_class, mid_confidence)]),
        )
        print_result("smoothing frame 2", engine.update([]))
        print_result(
            "smoothing frame 3",
            engine.update([Detection(danger_class, mid_confidence)]),
        )

        engine.reset()
        print_result("after reset", engine.update([]))

    except RailScanError as exc:
        print(f"Decision test failed: {exc}", file=sys.stderr)
        return 1

    print("Decision test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
