"""Benchmark raw RailScan Pro inference latency."""

from __future__ import annotations

import argparse
import statistics
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
    parser = argparse.ArgumentParser(description="Benchmark RailScan Pro inference.")
    parser.add_argument("--mock", action="store_true", help="Run without a real ONNX model.")
    parser.add_argument("--model", help="Path to an ONNX model.")
    parser.add_argument("--input-size", type=int, help="Model input size in pixels.")
    parser.add_argument("--runs", type=int, default=30, help="Measured inference runs.")
    parser.add_argument("--warmup", type=int, default=2, help="Warmup runs before measuring.")
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


def percentile(values: list[float], percentile_value: float) -> float:
    if len(values) == 1:
        return values[0]

    sorted_values = sorted(values)
    index = round((percentile_value / 100.0) * (len(sorted_values) - 1))
    return sorted_values[index]


def main() -> int:
    args = parse_args()

    if args.runs <= 0:
        print("--runs must be greater than zero.", file=sys.stderr)
        return 1
    if args.warmup < 0:
        print("--warmup cannot be negative.", file=sys.stderr)
        return 1

    latencies: list[float] = []

    try:
        inference_config = build_inference_config(args)
        frame = create_synthetic_frame()

        with RailScanInferenceEngine(inference_config) as engine:
            for _ in range(args.warmup):
                engine.run(frame)

            for _ in range(args.runs):
                result = engine.run(frame)
                latencies.append(result.latency_ms)

    except RailScanError as exc:
        print(f"Inference benchmark failed: {exc}", file=sys.stderr)
        return 1

    print(f"Mock mode: {inference_config.mock}")
    print(f"Runs: {args.runs}")
    print(f"Average latency ms: {statistics.fmean(latencies):.3f}")
    print(f"P50 latency ms: {percentile(latencies, 50):.3f}")
    print(f"P95 latency ms: {percentile(latencies, 95):.3f}")
    print(f"Min latency ms: {min(latencies):.3f}")
    print(f"Max latency ms: {max(latencies):.3f}")
    print("Inference benchmark completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
