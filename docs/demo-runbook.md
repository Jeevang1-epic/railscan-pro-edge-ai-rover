# Demo Runbook

This runbook is for a safe software demo of RailScan Pro.

## Install Runtime Dependencies

```bash
python -m pip install -r requirements.txt
```

Training dependencies are not needed for the safe demo.

## Run Final QA

```bash
python scripts/final_qa.py
python -m pytest
```

## Safe Default Demo

This command uses synthetic frames, mock inference, and serial dry-run:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Expected result:

- finite run
- no detections
- no STOP action
- `STOP actually sent: False`
- report at `runs/reports/runtime_summary.json`

## Simulated Defect Demo

This command injects one deterministic simulated defect into the safe runtime:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Expected result:

- finite run
- one simulated detection
- decision latches
- STOP action is dry-run only
- `STOP actually sent: False`

## Inspect Runtime Summary

Open:

```text
runs/reports/runtime_summary.json
```

Check:

- `frames_processed`
- `total_detections`
- `decision_latched`
- `stop_action_mode`
- `stop_actually_sent`
- `safety_flags`
- `runtime_mode`

## Optional Real Camera Dry-Run

Only run when a camera is connected:

```bash
python scripts/run_demo.py --camera-source 0 --mock-inference --serial-dry-run --frames 30
```

This still uses serial dry-run.

## Optional Real Model Dry-Run

Only run when `models/railscan_yolo.onnx` exists:

```bash
python scripts/run_demo.py --synthetic --model models/railscan_yolo.onnx --serial-dry-run --frames 10
```

This still uses serial dry-run.

## Optional Real Serial STOP

Only run after Arduino wiring is checked and the rover wheels are lifted:

```bash
python scripts/run_demo.py --synthetic --mock-inference --frames 5 --simulate-defect-frame 3 --serial-port COM3 --enable-real-stop --confirm-wheels-lifted
```

Real STOP must never be presented as validated unless this command, or an equivalent hardware command, was actually run.
