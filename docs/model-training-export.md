# Model Training And Export

Prompt 7 adds a no-hardware model-building workflow for RailScan Pro.

```text
dataset.yaml -> YOLO training -> best.pt -> ONNX export -> models/railscan_yolo.onnx
```

This workflow does not open a camera, send serial STOP, call Arduino firmware, or run the full rover loop.

## Dependencies

Base runtime dependencies stay in `requirements.txt`.

Training/export dependencies are isolated in `requirements-train.txt`:

```text
ultralytics
torch
onnx
onnxsim
```

Install them only when you are ready to run real training or real export.

## Dataset Template

The dataset template is:

```text
datasets/railscan_v1/data.yaml
```

It declares `nc: 5` and the same class order used by `model.class_names` in `config/railscan.yaml`.

Expected folders:

```text
datasets/railscan_v1/images/train
datasets/railscan_v1/images/val
datasets/railscan_v1/images/test
datasets/railscan_v1/labels/train
datasets/railscan_v1/labels/val
datasets/railscan_v1/labels/test
```

YOLO labels use:

```text
class_id x_center y_center width height
```

All box coordinates are normalized between `0.0` and `1.0`.

## Dry-Run Validation

These commands validate script configuration without requiring a GPU, dataset images, trained weights, or heavy training packages:

```bash
python scripts/train_yolo.py --dry-run
python scripts/export_onnx.py --dry-run
python scripts/validate_model_artifact.py --model models/railscan_yolo.onnx --allow-missing
```

## Real Training

Install training dependencies first:

```bash
python -m pip install -r requirements-train.txt
```

Then run training when the dataset is populated:

```bash
python scripts/train_yolo.py --data datasets/railscan_v1/data.yaml --model yolo11n.pt --imgsz 320 --epochs 50 --batch 16
```

The default output is:

```text
runs/train/railscan_yolo/weights/best.pt
```

## Real ONNX Export

Export after trained weights exist:

```bash
python scripts/export_onnx.py --weights runs/train/railscan_yolo/weights/best.pt --output models/railscan_yolo.onnx
```

Then validate the artifact:

```bash
python scripts/validate_model_artifact.py --model models/railscan_yolo.onnx
```

## Current Limitations

- Prompt 7 does not include a real labeled dataset.
- Prompt 7 does not run training or export during normal validation.
- Prompt 7 does not connect the model artifact to camera/inference/decision/STOP runtime behavior.
