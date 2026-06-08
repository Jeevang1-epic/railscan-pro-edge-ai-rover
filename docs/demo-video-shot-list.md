# Demo Video Shot List

Use this structure for a 60-120 second submission video.

## 0-10 Seconds: Project Title

Show:

- repository name: RailScan Pro
- Team Sentinals95
- one-sentence goal: proof-of-concept railway track inspection rover with guarded emergency-stop path

## 10-25 Seconds: Architecture

Show `README.md` or `docs/submission-summary.md`.

Say:

- Python handles camera/inference/detection/decision/runtime reporting foundations.
- Arduino handles motor cutoff and latched STOP.
- Current demo is safe software mode.

## 25-45 Seconds: Final QA

Show terminal command:

```bash
python scripts/final_qa.py
```

Show the successful output.

## 45-70 Seconds: Safe Runtime Demo

Show:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Point to:

- finite frame count
- no detections
- `STOP actually sent: False`

## 70-95 Seconds: Simulated Defect Demo

Show:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Point to:

- simulated detection
- decision latch
- dry-run STOP
- `STOP actually sent: False`

## 95-110 Seconds: Runtime Report

Show:

```text
runs/reports/runtime_summary.json
```

Highlight:

- `frames_processed`
- `decision_latched`
- `stop_action_mode`
- `stop_actually_sent`
- `safety_flags`

## 110-120 Seconds: Limitations And Next Steps

Say clearly:

- Real camera validation is pending.
- Real ONNX model validation is pending.
- Real Arduino STOP validation is pending.
- Hardware testing must be done with wheels lifted.

Optional hardware visuals may show the Arduino, L298N, rover chassis, or wiring, but do not describe those visuals as validation unless the hardware commands were actually run.
