# Serial STOP Foundation

Prompt 2 V2 adds the Python-to-Arduino emergency STOP bridge.

## Command

The emergency command is one byte:

```text
S
```

Python sends `b"S"` over USB serial. The Arduino accepts `S` or `s`, and the first `S` in `STOP` also latches the stop for Serial Monitor testing.

## Dry-Run Validation

Use dry-run mode when no Arduino is connected:

```bash
python scripts/serial_stop_test.py --dry-run
```

Dry-run mode loads `config/railscan.yaml`, prepares the STOP command, and prints what would be sent without opening a serial port.

## Hardware Validation

Only run this with the Arduino connected and the firmware uploaded:

```bash
python scripts/serial_stop_test.py --port COM3 --wait-ack
```

Use `/dev/ttyACM0` or the correct device path on Linux.

The Arduino acknowledgement is:

```text
EMERGENCY_STOP_LATCHED
```

The Arduino cuts PWM and direction pins before printing the acknowledgement. The STOP latch has no resume command in Prompt 2 V2; reset the Arduino to move again.

## Safety Notes

- Keep wheels lifted for first tests.
- Do not make acknowledgement mandatory for stopping; it is only confirmation after the stop action.
- The Python client avoids repeated STOP writes unless `force=True` is used.
- The CLI exposes `--force`, but normal STOP validation should not need it.
