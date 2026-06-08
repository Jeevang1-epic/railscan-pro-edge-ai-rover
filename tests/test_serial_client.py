from pathlib import Path

from railscan.config import load_config
from railscan.serial_client import (
    DEFAULT_STOP_COMMAND,
    RailScanSerialClient,
    SerialConfig,
)


class FakeSerial:
    def __init__(self, *args, **kwargs) -> None:
        self.is_open = True
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True
        self.is_open = False

    def readline(self) -> bytes:
        return b"EMERGENCY_STOP_LATCHED\n"


def test_dry_run_client_can_send_stop() -> None:
    client = RailScanSerialClient(SerialConfig(port="COM3", dry_run=True))

    result = client.send_stop()

    assert result.sent is True
    assert result.dry_run is True
    assert result.command == b"S"
    assert client.stop_sent is True


def test_default_stop_command_is_s() -> None:
    config = SerialConfig(port="COM3")
    client = RailScanSerialClient(config)

    assert config.stop_command == DEFAULT_STOP_COMMAND
    assert client.stop_command == b"S"


def test_repeated_stop_is_not_sent_twice_unless_forced() -> None:
    fake = FakeSerial()
    client = RailScanSerialClient(
        SerialConfig(port="COM3"),
        serial_factory=lambda **kwargs: fake,
    )

    first = client.send_stop()
    second = client.send_stop()
    forced = client.send_stop(force=True)

    assert first.sent is True
    assert second.sent is False
    assert second.skipped_duplicate is True
    assert forced.sent is True
    assert fake.writes == [b"S", b"S"]


def test_serial_client_can_close_safely() -> None:
    fake = FakeSerial()
    client = RailScanSerialClient(
        SerialConfig(port="COM3"),
        serial_factory=lambda **kwargs: fake,
    )

    client.connect()
    client.close()
    client.close()

    assert fake.closed is True


def test_client_can_be_constructed_from_config_values() -> None:
    app_config = load_config(Path("config") / "railscan.yaml")
    config = SerialConfig.from_mapping(app_config["serial"], dry_run=True)
    client = RailScanSerialClient(config)

    assert client.config.port == "COM3"
    assert client.config.baudrate == 115200
    assert client.config.ack_timeout_ms == 500
    assert client.config.dry_run is True
    assert client.stop_command == b"S"
