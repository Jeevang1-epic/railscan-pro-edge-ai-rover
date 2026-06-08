"""CLI utility for validating RailScan Pro raw ONNX inference."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.config import load_config  # noqa: E402
from railscan.exceptions import RailScanError  # noqa: E402
from railscan.inference import (  # noqa: E402
    InferenceConfig,
    RailScanInferenceEngine,
    create_synthetic_frame,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate RailScan Pro inference without decision logic."
    )
    parser.add_argument("--mock", action="store_true", help="Run without a real ONNX model.")
    parser.add_argument("--model", help="Path to an ONNX model.")
    parser.add_argument("--input-size", type=int, help="Model input size in pixels.")
    return parser.parse_args()


def build_inference_config(args: argparse.Namespace) -> InferenceConfig:
    config = load_config(REPO_ROOT / "config" / "railscan.yaml")
    model_config = dict(config["model"])

    model_path = args.model if args.model is not None else model_config.get("path")
    input_size = args.input_size if args.input_size is not None else None

    return InferenceConfig.from_mapping(
        model_config,
        model_path=model_path,
        input_size=input_size,
        mock=args.mock,
    )


def main() -> int:
    args = parse_args()

    try:
        inference_config = build_inference_config(args)
        frame = create_synthetic_frame()

        with RailScanInferenceEngine(inference_config) as engine:
            result = engine.run(frame)

    except RailScanError as exc:
        print(f"Inference test failed: {exc}", file=sys.stderr)
        return 1

    print(f"Mock mode: {inference_config.mock}")
    print(f"Model path: {inference_config.model_path}")
    print(f"Input shape: {result.input_shape}")
    print(f"Output shapes: {result.output_shapes}")
    print(f"Latency ms: {result.latency_ms:.3f}")
    print("Inference test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
