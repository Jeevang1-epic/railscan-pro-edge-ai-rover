# Submission Summary

## Problem Statement

Railway track inspection is repetitive, safety-critical, and difficult to scale with manual checks alone. RailScan Pro explores a low-cost rover approach for identifying visible track hazards and triggering a controlled emergency-stop path.

## Solution Summary

RailScan Pro is a proof-of-concept edge-AI railway inspection rover. The current repository demonstrates a safe software runtime using synthetic frames, mock inference, detection adaptation, pure decision logic, and dry-run STOP behavior.

## System Architecture

The project uses split logic:

- Python/local PC: camera frame handling, inference foundation, detection adaptation, decision logic, runtime reporting, and future serial STOP command.
- Arduino UNO: L298N motor control and latched emergency STOP behavior.

Real STOP is guarded. It is disabled by default and requires both `--enable-real-stop` and `--confirm-wheels-lifted`.

## Implemented Modules

- `src/railscan/config.py`: YAML config loading and validation
- `src/railscan/camera.py`: real/synthetic camera foundation
- `src/railscan/inference.py`: real/mock ONNX inference foundation
- `src/railscan/detection_adapter.py`: YOLO-like output adapter
- `src/railscan/decision.py`: pure decision engine
- `src/railscan/runtime.py`: safe finite runtime orchestration
- `src/railscan/serial_client.py`: dry-run capable serial STOP client
- `arduino/railscan_motor_controller/railscan_motor_controller.ino`: latched motor STOP firmware

## Safe Demo Status

The safe demo is ready:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

The simulated-defect run latches the decision path and records a dry-run STOP action without sending a real serial command.

## Simulated Vs Real Validation

Validated in safe software mode:

- synthetic frames
- mock inference
- detection adapter
- decision latch behavior
- dry-run STOP path
- runtime summary report

Not claimed as complete:

- real camera validation
- real trained ONNX model validation
- real Arduino serial STOP validation
- real model training/export

## Final Limitations

RailScan Pro v0.1.0 is a submission-ready proof-of-concept, not a certified operational safety system. It demonstrates the software architecture and safety gates, while real hardware and model validation remain future work.
