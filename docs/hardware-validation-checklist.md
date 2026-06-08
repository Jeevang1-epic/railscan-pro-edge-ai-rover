# Hardware Validation Checklist

Use this checklist only when the Arduino, motor driver, battery, and rover are physically prepared.

## Arduino Connection

- Upload `arduino/railscan_motor_controller/railscan_motor_controller.ino`.
- Confirm Arduino UNO is connected to the expected serial port.
- Confirm the configured baudrate is `115200`.
- Confirm the Arduino prints `EMERGENCY_STOP_LATCHED` after STOP is received.

## L298N Wiring

- ENA is connected to D5.
- IN1 is connected to D7.
- IN2 is connected to D8.
- ENB is connected to D6.
- IN3 is connected to D9.
- IN4 is connected to D10.
- Grounds are common between Arduino and motor power.
- Motor power polarity is checked before enabling motors.

## Motor Safety

- Lift the rover wheels before any real STOP test.
- Keep hands clear of wheels, belts, and exposed wiring.
- Keep a physical power cutoff available.
- Use `AUTO_START_MOTORS = false` for bench safety unless intentionally testing motion.
- Stop immediately if motor direction, speed, sound, heat, or wiring behavior is unexpected.

## Serial Port Identification

On Windows, confirm the Arduino port in Device Manager or Arduino IDE.

The default config uses:

```text
COM3
```

Use another port with `--serial-port` if needed.

## Dry-Run Before Real STOP

Run:

```bash
python scripts/serial_stop_test.py --dry-run
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Confirm both commands complete without hardware side effects.

## Real STOP Test

Only when wheels are lifted and the serial port is confirmed:

```bash
python scripts/run_demo.py --synthetic --mock-inference --frames 5 --simulate-defect-frame 3 --serial-port COM3 --enable-real-stop --confirm-wheels-lifted
```

Expected behavior:

- simulated defect triggers the decision path
- one STOP command is sent
- Arduino latches emergency stop
- PWM is cut to zero
- direction pins are LOW
- motors stop and remain stopped

Do not continue if any behavior differs from the expected result.
