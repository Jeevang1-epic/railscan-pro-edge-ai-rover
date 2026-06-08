# Arduino L298N Wiring

Prompt 2 V2 firmware targets Arduino UNO plus an L298N motor driver.

## Default Pin Mapping

| L298N Pin | Arduino UNO Pin | Purpose |
|---|---:|---|
| ENA | D5 | Left-side PWM |
| IN1 | D7 | Left direction |
| IN2 | D8 | Left direction |
| ENB | D6 | Right-side PWM |
| IN3 | D9 | Right direction |
| IN4 | D10 | Right direction |
| GND | GND | Common ground |

For a 4WD chassis, connect the left two motors to one L298N output channel and the right two motors to the other.

## Power Safety

- Do not power motors from the Arduino 5V pin.
- Use an external motor battery for the L298N motor supply.
- Connect Arduino GND, L298N GND, and battery GND together.
- Test with the rover wheels lifted before any floor test.

## Firmware Safety

The firmware lives at:

```text
arduino/railscan_motor_controller/railscan_motor_controller.ino
```

It starts with motors off and `AUTO_START_MOTORS` set to `false`. When it receives `S`, `s`, or `STOP`, it latches emergency stop, sets both PWM outputs to `0`, sets all direction pins `LOW`, and prints:

```text
EMERGENCY_STOP_LATCHED
```

There is no resume command in Prompt 2 V2.
