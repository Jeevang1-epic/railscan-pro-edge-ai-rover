# Judge Walkthrough

This guide helps reviewers inspect RailScan Pro without needing hardware.

## Start Here

Open `README.md` first. It explains the project goal, current stage, architecture, safe demo commands, and limitations.

Then review:

- `docs/submission-summary.md`
- `docs/release-notes-v0.1.0.md`
- `docs/demo-runbook.md`
- `docs/runtime-integration.md`
- `docs/hardware-validation-checklist.md`

## Commands To Run

Install base dependencies:

```bash
python -m pip install -r requirements.txt
```

Run final QA:

```bash
python scripts/final_qa.py
```

Expected output includes:

```text
Final QA checks passed.
```

Run the safe no-defect demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Expected output includes:

```text
Frames processed: 5
STOP actually sent: False
```

Run the simulated-defect demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Expected output includes:

```text
Decision latched: True
STOP action status: dry-run
STOP actually sent: False
```

Package review artifacts:

```bash
python scripts/package_demo_artifacts.py
```

Expected output includes:

```text
Demo submission package written to:
```

## Inspect Runtime Summary JSON

After a runtime command, open:

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
- `latency_summary`

## Verify STOP Safety Flags

Real STOP requires both flags:

```text
--enable-real-stop
--confirm-wheels-lifted
```

The source-level safety scans are:

```bash
python -c "from pathlib import Path; text = Path('scripts/run_demo.py').read_text(); assert '--enable-real-stop' in text and '--confirm-wheels-lifted' in text, 'Missing explicit real STOP safety flags'; print('run_demo.py safety flag scan passed')"
python -c "from pathlib import Path; text = Path('src/railscan/runtime.py').read_text(); assert 'enable_real_stop' in text and 'confirm_wheels_lifted' in text, 'runtime.py missing real STOP guard fields'; print('runtime.py STOP guard scan passed')"
```

## What Not To Claim

Do not claim completion of:

- physical rover validation
- live camera validation
- real ONNX model validation
- real model training
- safety certification for railway operation

Use the current wording: proof-of-concept, safe software demo, mock inference, dry-run STOP, hardware/model validation pending.
