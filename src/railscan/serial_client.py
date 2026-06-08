"""Serial emergency-stop client for RailScan Pro."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from railscan.exceptions import SerialClientError

DEFAULT_STOP_COMMAND = "S"
DEFAULT_ACK = "EMERGENCY_STOP_LATCHED"


class SerialConnection(Protocol):
    """Minimal pyserial-compatible interface used by the client and tests."""

    is_open: bool

    def write(self, data: bytes) -> int | None:
        ...

    def flush(self) -> None:
        ...

    def close(self) -> None:
        ...

    def readline(self) -> bytes:
        ...


@dataclass(frozen=True)
class SerialConfig:
    """Configuration needed to send an Arduino emergency STOP."""

    port: str
    baudrate: int = 115200
    stop_command: str = DEFAULT_STOP_COMMAND
    ack_timeout_ms: int = 500
    expected_ack: str = DEFAULT_ACK
    dry_run: bool = False

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, Any],
        *,
        dry_run: bool = False,
    ) -> "SerialConfig":
        """Build serial config from the `serial` section of railscan.yaml."""

        try:
            port = str(values["port"]).strip()
        except KeyError as exc:
            raise SerialClientError("Serial config is missing required key: port.") from exc

        if not port:
            raise SerialClientError("Serial config port cannot be empty.")

        return cls(
            port=port,
            baudrate=_read_int(values, "baudrate", 115200),
            stop_command=str(values.get("stop_command", DEFAULT_STOP_COMMAND)),
            ack_timeout_ms=_read_int(values, "ack_timeout_ms", 500),
            expected_ack=str(values.get("expected_ack", DEFAULT_ACK)),
            dry_run=dry_run,
        )


@dataclass(frozen=True)
class StopResult:
    """Result returned after attempting to send STOP."""

    sent: bool
    command: bytes
    dry_run: bool
    skipped_duplicate: bool = False


class RailScanSerialClient:
    """Send a latched STOP command to an Arduino over serial."""

    def __init__(
        self,
        config: SerialConfig,
        *,
        serial_factory: Callable[..., SerialConnection] | None = None,
    ) -> None:
        self.config = config
        self._stop_command_bytes = _encode_single_byte(config.stop_command)
        self._serial_factory = serial_factory
        self._connection: SerialConnection | None = None
        self._stop_sent = False

    @classmethod
    def from_values(
        cls,
        *,
        port: str,
        baudrate: int = 115200,
        stop_command: str = DEFAULT_STOP_COMMAND,
        ack_timeout_ms: int = 500,
        expected_ack: str = DEFAULT_ACK,
        dry_run: bool = False,
        serial_factory: Callable[..., SerialConnection] | None = None,
    ) -> "RailScanSerialClient":
        """Create a client without manually constructing SerialConfig."""

        config = SerialConfig(
            port=port,
            baudrate=baudrate,
            stop_command=stop_command,
            ack_timeout_ms=ack_timeout_ms,
            expected_ack=expected_ack,
            dry_run=dry_run,
        )
        return cls(config, serial_factory=serial_factory)

    @property
    def is_connected(self) -> bool:
        if self.config.dry_run:
            return True
        return self._connection is not None and self._connection.is_open

    @property
    def stop_command(self) -> bytes:
        return self._stop_command_bytes

    @property
    def stop_sent(self) -> bool:
        return self._stop_sent

    def connect(self) -> "RailScanSerialClient":
        """Open serial unless dry-run mode is active."""

        if self.config.dry_run or self.is_connected:
            return self

        serial_factory = self._serial_factory or _load_pyserial_factory()

        try:
            self._connection = serial_factory(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.ack_timeout_ms / 1000,
                write_timeout=self.config.ack_timeout_ms / 1000,
            )
        except Exception as exc:
            raise SerialClientError(
                f"Unable to open serial port {self.config.port!r} "
                f"at {self.config.baudrate} baud."
            ) from exc

        return self

    def send_stop(self, *, force: bool = False) -> StopResult:
        """Send STOP once. Use force=True only for an intentional resend."""

        if self._stop_sent and not force:
            return StopResult(
                sent=False,
                command=self.stop_command,
                dry_run=self.config.dry_run,
                skipped_duplicate=True,
            )

        if self.config.dry_run:
            self._stop_sent = True
            return StopResult(
                sent=True,
                command=self.stop_command,
                dry_run=True,
            )

        self.connect()
        connection = self._require_connection()

        try:
            bytes_written = connection.write(self.stop_command)
            connection.flush()
        except Exception as exc:
            raise SerialClientError("Failed to send STOP command over serial.") from exc

        if bytes_written is not None and bytes_written != len(self.stop_command):
            raise SerialClientError(
                "Incomplete STOP write: "
                f"wrote {bytes_written} of {len(self.stop_command)} bytes."
            )

        self._stop_sent = True
        return StopResult(
            sent=True,
            command=self.stop_command,
            dry_run=False,
        )

    def wait_for_ack(self) -> str | None:
        """Wait for the configured Arduino acknowledgement line."""

        if self.config.dry_run:
            return self.config.expected_ack

        connection = self._require_connection()
        deadline = time.monotonic() + (self.config.ack_timeout_ms / 1000)

        while time.monotonic() < deadline:
            try:
                raw_line = connection.readline()
            except Exception as exc:
                raise SerialClientError("Failed while reading serial acknowledgement.") from exc

            if not raw_line:
                continue

            line = raw_line.decode("utf-8", errors="replace").strip()
            if line == self.config.expected_ack:
                return line

        return None

    def close(self) -> None:
        """Close serial safely. Calling close more than once is allowed."""

        if self._connection is None:
            return

        try:
            if self._connection.is_open:
                self._connection.close()
        except Exception as exc:
            raise SerialClientError("Failed to close serial connection.") from exc
        finally:
            self._connection = None

    def _require_connection(self) -> SerialConnection:
        if self._connection is None or not self._connection.is_open:
            raise SerialClientError("Serial client is not connected.")
        return self._connection

    def __enter__(self) -> "RailScanSerialClient":
        return self.connect()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: Any,
    ) -> None:
        self.close()


def _encode_single_byte(command: str) -> bytes:
    if not command:
        raise SerialClientError("STOP command cannot be empty.")

    try:
        encoded = command.encode("ascii")
    except UnicodeEncodeError as exc:
        raise SerialClientError("STOP command must be ASCII.") from exc

    if len(encoded) != 1:
        raise SerialClientError("STOP command must be exactly one byte.")

    return encoded


def _read_int(values: Mapping[str, Any], key: str, default: int) -> int:
    try:
        return int(values.get(key, default))
    except (TypeError, ValueError) as exc:
        raise SerialClientError(f"Serial config value {key!r} must be an integer.") from exc


def _load_pyserial_factory() -> Callable[..., SerialConnection]:
    try:
        import serial
    except ImportError as exc:
        raise SerialClientError(
            "pyserial is required for real serial mode. Install requirements.txt first."
        ) from exc

    return serial.Serial
