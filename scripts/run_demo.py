"""Run the RailScan Pro safe integrated demo pipeline."""

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
from railscan.runtime import RailScanRuntime, RuntimeConfig  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the safe RailScan demo pipeline.")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--synthetic", action="store_true", default=None)
    parser.add_argument("--camera-source")
    parser.add_argument("--mock-inference", action="store_true", default=None)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--serial-port")
    parser.add_argument("--serial-dry-run", action="store_true", default=None)
    parser.add_argument("--enable-real-stop", action="store_true")
    parser.add_argument("--confirm-wheels-lifted", action="store_true")
    parser.add_argument("--simulate-defect-frame", type=int)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def build_runtime_config(args: argparse.Namespace, config: dict) -> RuntimeConfig:
    synthetic = args.synthetic
    if synthetic is None and args.camera_source is not None:
        synthetic = False

    mock_inference = args.mock_inference
    if mock_inference is None and args.model is not None:
        mock_inference = False

    serial_dry_run = args.serial_dry_run
    if serial_dry_run is None and (args.enable_real_stop or args.confirm_wheels_lifted):
        serial_dry_run = False

    return RuntimeConfig.from_app_config(
        config,
        frames=args.frames,
        synthetic=synthetic,
        camera_source=args.camera_source,
        mock_inference=mock_inference,
        model_path=args.model,
        serial_port=args.serial_port,
        serial_dry_run=serial_dry_run,
        enable_real_stop=args.enable_real_stop,
        confirm_wheels_lifted=args.confirm_wheels_lifted,
        simulate_defect_frame=args.simulate_defect_frame,
        output_dir=args.output_dir,
    )


def print_summary(summary) -> None:
    print("RailScan runtime completed.")
    print(f"Runtime mode: {summary.runtime_mode}")
    print(f"Frames processed: {summary.frames_processed}")
    print(f"Total detections: {summary.total_detections}")
    print(f"Decision latched: {summary.decision_latched}")
    print(f"STOP action status: {summary.stop_action_mode}")
    print(f"STOP actually sent: {summary.stop_actually_sent}")
    print(f"Summary report: {summary.report_path}")


def main() -> int:
    args = parse_args()

    try:
        config = load_config(REPO_ROOT / "config" / "railscan.yaml")
        runtime_config = build_runtime_config(args, config)
        runtime = RailScanRuntime(runtime_config, config)
        summary = runtime.run()
        print_summary(summary)

    except RailScanError as exc:
        print(f"RailScan runtime failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
