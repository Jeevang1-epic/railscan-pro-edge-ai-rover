# RailScan Pro

RailScan Pro is a proof-of-concept edge-AI railway track inspection rover by Team Sentinals95 for Makers Conclave 2026.

The project demonstrates a local, safety-first inspection pipeline: capture frames, run model inference, convert detections, make a stop decision, and keep the motor emergency-stop path guarded through Arduino-controlled actuation.

The repository is currently ready for a safe software demo using synthetic frames, mock inference, and serial dry-run mode. Real camera, model, and Arduino validation are intentionally separated so they can be tested only when the hardware and model artifacts are prepared.

## What It Does

- Loads project settings from `config/railscan.yaml`
- Provides synthetic and OpenCV camera capture modes
- Provides mock and ONNX Runtime inference modes
- Converts YOLO-like model outputs into normalized detections
- Applies pure decision logic with danger classes, confidence thresholds, temporal smoothing, and latching
- Runs a finite safe demo pipeline that writes a runtime summary JSON report
- Supports dry-run serial STOP testing without Arduino hardware
- Provides Arduino UNO firmware for a latched L298N emergency stop
- Includes dry-run YOLO training/export helpers and a dataset template
- Includes tests and documentation for safe review and demo recording

## Architecture

```text
Camera source
  -> Inference engine
  -> Detection adapter
  -> Decision engine
  -> Guarded STOP action
  -> Runtime report
```

RailScan Pro uses split logic:

- Python/local PC: camera capture, inference, detection post-processing, decision logic, runtime reporting, and serial STOP client
- Arduino UNO: L298N motor control and latched motor cutoff

The emergency command is a single byte:

```text
S
```

The Arduino firmware latches STOP, cuts PWM to zero, sets all direction pins LOW, and prints:

```text
EMERGENCY_STOP_LATCHED
```

Real STOP is disabled by default. It requires both explicit safety flags:

```text
--enable-real-stop
--confirm-wheels-lifted
```

## Repository Layout

```text
arduino/                         Arduino UNO motor controller firmware
config/                          Runtime configuration
datasets/                        Dataset template and notes
docs/                            Setup, demo, validation, and submission docs
models/                          Model artifact placeholder and notes
runs/                            Runtime outputs, ignored except .gitkeep
scripts/                         CLI validation, demo, training, export, and packaging tools
src/railscan/                    Python package source
tests/                           Unit tests
```

## Requirements

- Python 3.10+
- Windows, Linux, or macOS
- Base Python dependencies from `requirements.txt`
- Optional Arduino UNO + L298N motor driver for hardware STOP validation
- Optional ONNX model at `models/railscan_yolo.onnx` for real model inference
- Optional training dependencies from `requirements-train.txt`

Base dependencies are intentionally lightweight for the safe demo. Training dependencies are kept separate.

## Setup

Create and activate a virtual environment if desired, then install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the smoke check:

```bash
python scripts/smoke_check.py
```

## Safe Software Demo

Run the default no-hardware demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Run a deterministic simulated-defect demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Expected behavior:

- The run is finite.
- Frames are synthetic.
- Inference is mock mode.
- STOP remains dry-run only.
- No serial STOP command is sent.
- A summary report is written to `runs/reports/runtime_summary.json`.

## Validation

Run the core validation suite:

```bash
python scripts/final_qa.py
python scripts/package_demo_artifacts.py
python -m pytest
python -m compileall src scripts
```

Run individual module checks:

```bash
python scripts/serial_stop_test.py --dry-run
python scripts/camera_test.py --synthetic --frames 5
python scripts/inference_test.py --mock
python scripts/benchmark_inference.py --mock --runs 5
python scripts/detection_test.py
python scripts/decision_test.py
```

These checks do not require Arduino hardware, a webcam, a trained model, a GPU, dataset images, or training dependencies.

## Configuration

Main configuration lives in:

```text
config/railscan.yaml
```

Important sections:

- `camera`: frame source, resolution, model input size
- `serial`: serial port, baudrate, STOP command, expected Arduino acknowledgement
- `model`: model path, thresholds, class names, inference provider
- `postprocessing`: detection adapter settings
- `decision`: smoothing window and required hit count
- `runtime`: default safe runtime mode and report output directory
- `training` / `export`: YOLO training and ONNX export defaults

## Runtime Report

The integrated demo writes:

```text
runs/reports/runtime_summary.json
```

The report includes:

- frames processed
- total detections
- decision latch state
- STOP action mode
- whether STOP was actually sent
- runtime mode
- safety flags
- latency summary

## Camera

Synthetic camera validation:

```bash
python scripts/camera_test.py --synthetic --frames 5
```

Optional real camera check:

```bash
python scripts/camera_test.py --source 0 --frames 30
```

Use the real camera command only when a camera is connected. See `docs/camera-setup.md`.

## Inference

Mock inference validation:

```bash
python scripts/inference_test.py --mock
```

Optional real ONNX validation, only when the model file exists:

```bash
python scripts/inference_test.py --model models/railscan_yolo.onnx
python scripts/benchmark_inference.py --model models/railscan_yolo.onnx --runs 30
```

See `docs/inference-setup.md`.

## Training And Export

Training dependencies are isolated in:

```text
requirements-train.txt
```

Dry-run training/export checks:

```bash
python scripts/train_yolo.py --dry-run
python scripts/export_onnx.py --dry-run
python scripts/validate_model_artifact.py --model models/railscan_yolo.onnx --allow-missing
```

Real training requires a populated YOLO dataset under `datasets/railscan_v1/`. See `docs/model-training-export.md`.

## Arduino STOP Hardware

Firmware:

```text
arduino/railscan_motor_controller/railscan_motor_controller.ino
```

Default L298N pins:

```text
ENA = D5
IN1 = D7
IN2 = D8
ENB = D6
IN3 = D9
IN4 = D10
```

Dry-run serial STOP test:

```bash
python scripts/serial_stop_test.py --dry-run
```

Hardware STOP validation should only be run after firmware upload, wiring checks, and lifting the rover wheels:

```bash
python scripts/serial_stop_test.py --port COM3 --wait-ack
```

For the integrated runtime, real STOP requires both safety flags:

```bash
python scripts/run_demo.py --synthetic --mock-inference --frames 5 --simulate-defect-frame 3 --serial-port COM3 --enable-real-stop --confirm-wheels-lifted
```

See `docs/serial-stop.md`, `docs/arduino-wiring.md`, and `docs/hardware-validation-checklist.md`.

## Submission Package

Generate a lightweight local review package:

```bash
python scripts/package_demo_artifacts.py
```

Output:

```text
dist/demo-submission/
```

The package contains a manifest and selected review documents. It excludes model binaries, dataset images, cache files, and runtime logs.

## Documentation

- `docs/demo-runbook.md`: safe demo commands and expected outputs
- `docs/runtime-integration.md`: integrated runtime behavior and safety gates
- `docs/final-qa-checklist.md`: final software and safety checklist
- `docs/hardware-validation-checklist.md`: hardware STOP validation checklist
- `docs/model-training-export.md`: dataset, training, and export workflow
- `docs/submission-summary.md`: project summary for reviewers
- `docs/judge-walkthrough.md`: reviewer walkthrough and expected outputs
- `docs/demo-video-shot-list.md`: suggested short demo recording sequence
- `docs/evidence-capture-checklist.md`: evidence collection checklist

## Current Limitations

- No trained model weights are committed.
- No real dataset images are committed.
- Real camera validation is pending.
- Real ONNX model validation is pending.
- Real Arduino serial STOP validation is pending.
- The default demo uses mock inference and dry-run STOP.
- This is a proof-of-concept prototype, not an operational railway safety system.

## Next Steps

1. Collect and label real track images using the class order in `datasets/railscan_v1/data.yaml`.
2. Train and export a real ONNX model.
3. Validate the ONNX model with real inference commands.
4. Validate real camera capture.
5. Upload Arduino firmware and validate STOP with rover wheels lifted.
6. Record real validation results in `docs/demo-report-template.md`.


---

## 👥 Team Sentinals95

<p align="center">
  <b>RailScan Pro: Contactless Track Monitoring</b><br/>
  <sub>Built for Makers Conclave 2026 · Problem Statement MC-15</sub>
</p>

<p align="center">
  🚆 ━━━━━━━━━━━━━━━━━━━━━━━ <b>Edge-AI Railway Inspection Rover</b> ━━━━━━━━━━━━━━━━━━━━━━━ 🚆
</p>

| Name | NIAT ID | Institution | Branch | Role |
|---|---|---|---|---|
| **Puttala Jeevan Kumar** | `N25H01A0181` | NIAT (CDU) | CSE (AI/ML) | Team Leader · Software Architecture · Edge-AI Pipeline |
| **Syed Mazhar Ali** | `N25H01A0135` | NIAT (CDU) | CSE (AI/ML) | Hardware Prototype · Arduino/L298N Integration |
| **Majeti Harshit** | `N25H01A0170` | NIAT (CDU) | CSE (AI/DS) | Prototype Support · Documentation |
| **Syed Mohammed Mustajab Abedi** | `N25H01A1051` | NIAT (CDU) | CSE (AI/DS) | Prototype Support · Validation |

### Project Contribution Summary

- **System Design:** Split-logic architecture with laptop/edge-device vision and Arduino motor control.
- **Software:** Camera pipeline, ONNX-ready inference, detection adapter, safety decision engine, and safe runtime demo.
- **Hardware:** 4WD rover chassis, Arduino UNO, L298N motor driver, DC gear motors, and serial STOP pathway.
- **Safety:** Real STOP disabled by default; dry-run validation and explicit safety flags used before hardware testing.

<p align="center">
  <i>“Detect locally. Decide safely. Stop responsibly.”</i>
</p>
