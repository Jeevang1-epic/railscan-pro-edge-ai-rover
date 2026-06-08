# Demo Report Template

Use this template to record a demo or validation session.

## Session

- Date:
- Presenter:
- Commit hash:
- Machine/OS:
- Python version:

## Commands Run

```text
python -m pip install -r requirements.txt
python scripts/final_qa.py
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
python -m pytest
```

## Validation Outputs

- `python scripts/final_qa.py`:
- safe default demo:
- simulated defect demo:
- `python -m pytest`:
- `python -m compileall src scripts`:

## Runtime Report

- Report path: `runs/reports/runtime_summary.json`
- Frames processed:
- Total detections:
- Decision latched:
- STOP action mode:
- STOP actually sent:

## Demo Evidence

- Terminal screenshot:
- Runtime report screenshot:
- Demo video:
- Hardware photos, if any:

## Hardware Status

- Real camera validation: not run / passed / failed
- Real ONNX model validation: not run / passed / failed
- Real Arduino STOP validation: not run / passed / failed
- Wheels lifted during real STOP test: yes / no / not applicable

## Known Limitations

- Real model status:
- Dataset status:
- Camera status:
- Serial hardware status:
- Any observed issues:

## Next Steps

- Dataset/model:
- Hardware:
- Demo polish:
- Risks to resolve:
