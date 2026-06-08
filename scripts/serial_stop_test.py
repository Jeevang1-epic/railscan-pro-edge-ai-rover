"""CLI utility for validating the RailScan Pro serial STOP path."""

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
from railscan.serial_client import RailScanSerialClient, SerialConfig  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send the RailScan Pro Arduino emergency STOP command."
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not open serial hardware.")
    parser.add_argument("--port", help="Serial port, for example COM3 or /dev/ttyACM0.")
    parser.add_argument("--baudrate", type=int, help="Serial baud rate.")
    parser.add_argument("--command", help="Single-byte STOP command. Default: S.")
    parser.add_argument("--wait-ack", action="store_true", help="Wait for Arduino ACK.")
    parser.add_argument("--force", action="store_true", help="Force send even if already sent.")
    return parser.parse_args()


def build_serial_config(args: argparse.Namespace) -> SerialConfig:
    config = load_config(REPO_ROOT / "config" / "railscan.yaml")
    serial_config = dict(config["serial"])

    if args.port is not None:
        serial_config["port"] = args.port
    if args.baudrate is not None:
        serial_config["baudrate"] = args.baudrate
    if args.command is not None:
        serial_config["stop_command"] = args.command

    return SerialConfig.from_mapping(serial_config, dry_run=args.dry_run)


def main() -> int:
    args = parse_args()

    try:
        serial_config = build_serial_config(args)
        with RailScanSerialClient(serial_config) as client:
            result = client.send_stop(force=args.force)

            if result.skipped_duplicate:
                print("STOP command already sent; duplicate write skipped.")
            elif result.dry_run:
                print(
                    "Dry run: would send STOP command "
                    f"{result.command!r} to {serial_config.port} "
                    f"at {serial_config.baudrate} baud."
                )
            else:
                print(
                    f"Sent STOP command {result.command!r} "
                    f"to {serial_config.port} at {serial_config.baudrate} baud."
                )

            if args.wait_ack:
                ack = client.wait_for_ack()
                if ack is None:
                    print(
                        "STOP sent, but acknowledgement "
                        f"{serial_config.expected_ack!r} was not received within "
                        f"{serial_config.ack_timeout_ms} ms."
                    )
                    return 1
                print(f"Arduino acknowledgement received: {ack}")

    except RailScanError as exc:
        print(f"Serial STOP test failed: {exc}", file=sys.stderr)
        return 1

    print("Serial STOP test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
