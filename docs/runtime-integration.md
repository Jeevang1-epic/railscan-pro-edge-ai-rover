# Runtime Integration

Prompt 8 adds the first safe end-to-end runtime path:

```text
frame source -> inference -> detection adapter -> decision engine -> guarded STOP action -> report
```

The default mode is safe:

```text
synthetic frames + mock inference + serial dry-run + finite frame count
```

Real serial STOP is disabled by default.

## Dry-Run Demo

Run the basic no-hardware pipeline:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Run a deterministic simulated defect:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

The simulated defect is for validation only. It creates a deterministic adapter-compatible detection so the decision and STOP-action paths can be tested without a camera or model.

The simulated defect frame must be within the finite run range. For example, `--frames 6 --simulate-defect-frame 3` is valid, while a simulated frame greater than the frame count is rejected.

## Report Output

The runtime writes:

```text
runs/reports/runtime_summary.json
```

The report includes:

- frames processed
- total detections
- decision latch state
- STOP action mode
- safety flags
- runtime mode
- latency summary

Report paths are written relative to the repository when possible, so the JSON does not depend on a user-specific absolute workspace path.

## Optional Real Camera Or Model

Only run a real camera dry-run when a camera is available:

```bash
python scripts/run_demo.py --camera-source 0 --mock-inference --serial-dry-run --frames 30
```

Only run a real model dry-run when `models/railscan_yolo.onnx` exists:

```bash
python scripts/run_demo.py --synthetic --model models/railscan_yolo.onnx --serial-dry-run --frames 10
```

## Real STOP Safety Gate

Real STOP requires both flags:

```text
--enable-real-stop
--confirm-wheels-lifted
```

If either flag is missing, the runtime blocks real STOP. Passing only one flag is treated as an incomplete real-STOP attempt and is reported as `blocked`, not sent. For hardware testing, the rover wheels must be lifted and the Arduino wiring must already be validated.

Example hardware command, only when explicitly intended:

```bash
python scripts/run_demo.py --synthetic --mock-inference --frames 5 --simulate-defect-frame 3 --serial-port COM3 --enable-real-stop --confirm-wheels-lifted
```

## Current Limitations

- Prompt 8 does not validate a real camera, real ONNX model, or real serial hardware by default.
- Prompt 8 does not add ROS2, dashboards, databases, cloud services, or Arduino firmware changes.
- Mock inference uses deterministic YOLO-like runtime outputs so the adapter and decision path can be tested without a trained model.
