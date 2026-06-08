"""CLI utility for validating RailScan Pro detection postprocessing."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.detection_adapter import (  # noqa: E402
    DetectionAdapterConfig,
    YoloDetectionAdapter,
)
from railscan.exceptions import RailScanError  # noqa: E402


def build_mock_output(class_count: int) -> np.ndarray:
    """Create deterministic YOLO-like rows with cx, cy, w, h, class scores."""

    rows = np.zeros((4, 4 + class_count), dtype=np.float32)

    rows[0, :4] = (100.0, 80.0, 40.0, 20.0)
    rows[0, 4] = 0.92

    rows[1, :4] = (102.0, 81.0, 40.0, 20.0)
    rows[1, 4] = 0.88

    if class_count > 1:
        rows[2, :4] = (220.0, 140.0, 60.0, 50.0)
        rows[2, 5] = 0.86
    else:
        rows[2, :4] = (220.0, 140.0, 60.0, 50.0)
        rows[2, 4] = 0.86

    rows[3, :4] = (40.0, 40.0, 10.0, 10.0)
    rows[3, 4] = 0.10

    return rows[np.newaxis, :, :]


def main() -> int:
    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
        adapter_config = DetectionAdapterConfig.from_app_config(config)
        adapter = YoloDetectionAdapter(adapter_config)
        raw_output = build_mock_output(len(adapter_config.class_names))
        detections = adapter.parse((raw_output,))

        print(f"Raw candidates: {raw_output.shape[1]}")
        print(f"Parsed detections: {len(detections)}")
        for index, detection in enumerate(detections, start=1):
            print(
                f"{index}: class={detection.class_name}, "
                f"confidence={detection.confidence:.3f}, "
                f"bbox={detection.bbox}"
            )

    except RailScanError as exc:
        print(f"Detection test failed: {exc}", file=sys.stderr)
        return 1

    print("Detection test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
