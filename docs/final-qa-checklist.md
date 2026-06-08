# Final QA Checklist

Use this checklist before a GitHub review, mentor walkthrough, or Makers Conclave demo.

## Software Validation

- Install base runtime dependencies with `python -m pip install -r requirements.txt`.
- Run `python scripts/final_qa.py`.
- Run both safe runtime demos:
  - `python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5`
  - `python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3`
- Run `python -m pytest`.
- Run `python -m compileall src scripts`.
- Confirm `runs/reports/runtime_summary.json` is created after the demo.

## Safety Checklist

- Keep `--serial-dry-run` enabled for normal demos.
- Do not use real STOP unless the rover wheels are lifted.
- Real STOP requires both `--enable-real-stop` and `--confirm-wheels-lifted`.
- Never claim real hardware validation unless the hardware command was actually run.
- Stop immediately if motor wiring, direction, or PWM behavior is unexpected.

## Repo Cleanliness

- Check `git status --short --branch`.
- Confirm no model weights, large datasets, or runtime logs are staged accidentally.
- Confirm `requirements.txt` does not include training-only dependencies.
- Confirm `requirements-train.txt` contains training/export dependencies.

## Demo Readiness

- Open `docs/demo-runbook.md`.
- Prepare the safe demo commands.
- Prepare a screenshot or terminal capture of the simulated defect run.
- Prepare the architecture explanation from `docs/demo-script.md`.

## No False Claims

- Describe RailScan Pro as a proof-of-concept edge-AI inspection rover.
- Say visible defect detection, not hidden micro-fracture detection.
- Say mock inference / dry-run demo until a real ONNX model is validated.
- Say hardware validation pending unless real camera, Arduino, and serial tests were run.
- Do not describe this as certified for railway safety.
