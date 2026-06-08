# Models

Place exported ONNX model artifacts here when they are available.

The default inference config expects:

```text
models/railscan_yolo.onnx
```

Model files are intentionally not committed yet. Real training/export and real model validation happen only when a dataset and trained weights are available.

Prompt 7 adds the expected training/export path:

```text
runs/train/railscan_yolo/weights/best.pt -> models/railscan_yolo.onnx
```

Use:

```bash
python scripts/validate_model_artifact.py --model models/railscan_yolo.onnx --allow-missing
```

Remove `--allow-missing` after the ONNX artifact exists and should be required.

Record real model validation results in `docs/demo-report-template.md`. Do not claim real ONNX validation passed until the model artifact exists and the real-model validation command has been run.
