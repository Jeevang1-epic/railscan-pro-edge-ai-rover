# Evidence Capture Checklist

Use this checklist before final submission or judge review.

## Repository Evidence

- Current commit hash:
- GitHub URL:
- Branch:
- `git status --short --branch` output:

## Validation Output Evidence

Capture terminal output for:

```bash
python -m pip install -r requirements.txt
python scripts/smoke_check.py
python scripts/final_qa.py
python scripts/package_demo_artifacts.py
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
python -m pytest
python -m compileall src scripts
```

Record the pytest result:

```text
pytest count:
```

## Runtime Report Evidence

Capture:

```text
runs/reports/runtime_summary.json
```

Record:

- frames processed:
- total detections:
- decision latched:
- stop action mode:
- stop actually sent:
- safety flags:

## Package Evidence

Run:

```bash
python scripts/package_demo_artifacts.py
```

Capture:

- `dist/demo-submission/manifest.json`
- copied review docs under `dist/demo-submission/docs/`
- package script terminal output

## Visual Evidence

- README screenshot:
- final QA terminal screenshot:
- safe demo terminal screenshot:
- simulated defect terminal screenshot:
- runtime summary JSON screenshot:
- optional hardware photo:
- optional short GIF/video:

## Skipped Validation Notes

Mark each one honestly:

- Real camera validation: not run / run
- Real ONNX model validation: not run / run
- Real Arduino serial STOP validation: not run / run
- Real training/export validation: not run / run

## Future Physical Validation Plan

- Upload Arduino firmware.
- Confirm L298N wiring.
- Lift rover wheels.
- Run serial dry-run first.
- Run real STOP only with both required safety flags.
- Record command output and hardware behavior in `docs/demo-report-template.md`.
