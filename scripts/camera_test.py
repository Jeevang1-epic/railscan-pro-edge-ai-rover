"""CLI utility for validating RailScan Pro camera capture."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from railscan.camera import CameraConfig, RailScanCamera  # noqa: E402
from railscan.config import load_config  # noqa: E402
from railscan.exceptions import RailScanError  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate RailScan Pro camera capture without AI inference."
    )
    parser.add_argument("--source", help="Camera index, file path, or stream URL.")
    parser.add_argument("--width", type=int, help="Requested frame width.")
    parser.add_argument("--height", type=int, help="Requested frame height.")
    parser.add_argument("--frames", type=int, default=10, help="Finite frame count to read.")
    parser.add_argument("--display", action="store_true", help="Show frames in an OpenCV window.")
    parser.add_argument("--synthetic", action="store_true", help="Generate frames without hardware.")
    return parser.parse_args()


def build_camera_config(args: argparse.Namespace) -> CameraConfig:
    config = load_config(REPO_ROOT / "config" / "railscan.yaml")
    camera_config = dict(config["camera"])

    if args.source is not None:
        camera_config["source"] = args.source
    if args.width is not None:
        camera_config["width"] = args.width
    if args.height is not None:
        camera_config["height"] = args.height

    return CameraConfig.from_mapping(camera_config, synthetic=args.synthetic)


def main() -> int:
    args = parse_args()

    if args.frames <= 0:
        print("--frames must be greater than zero.", file=sys.stderr)
        return 1

    cv2 = None
    if args.display:
        try:
            import cv2 as cv2_module
        except ImportError:
            print("Display mode requires opencv-python.", file=sys.stderr)
            return 1
        cv2 = cv2_module

    last_result = None

    try:
        camera_config = build_camera_config(args)
        with RailScanCamera(camera_config) as camera:
            for _ in range(args.frames):
                last_result = camera.read()

                if cv2 is not None:
                    cv2.imshow("RailScan Camera Test", last_result.frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

    except RailScanError as exc:
        print(f"Camera test failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if cv2 is not None:
            cv2.destroyAllWindows()

    if last_result is None:
        print("Camera test failed: no frames were read.", file=sys.stderr)
        return 1

    print(f"Camera source: {camera_config.source!r}")
    print(f"Synthetic mode: {camera_config.synthetic}")
    print(f"Frames read: {last_result.frame_index}")
    print(f"Last frame shape: {last_result.frame.shape}")
    fps_message = (
        f"Approx FPS: {last_result.fps:.2f}"
        if last_result.fps
        else "Approx FPS: unavailable"
    )
    print(fps_message)
    print(f"Display enabled: {args.display}")
    print("Camera test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
