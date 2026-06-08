# ONNX Inference Setup

Prompt 4 adds the raw ONNX inference foundation only. It does not implement defect decisions and does not send serial STOP commands.

## Mock Validation

Use mock mode when no ONNX model is available:

```bash
python scripts/inference_test.py --mock
python scripts/benchmark_inference.py --mock --runs 5
```

Mock mode creates a synthetic frame, exercises preprocessing, returns deterministic raw output arrays, and reports latency.

## Real ONNX Validation

Place a real exported ONNX model at:

```text
models/railscan_yolo.onnx
```

Then run:

```bash
python scripts/inference_test.py --model models/railscan_yolo.onnx
python scripts/benchmark_inference.py --model models/railscan_yolo.onnx --runs 30
```

Do not treat real model validation as passed unless those commands were actually run with a valid ONNX file.

## Configuration

Model defaults live in `config/railscan.yaml`:

```yaml
model:
  path: "models/railscan_yolo.onnx"
  input_size: 320
  providers:
    - CPUExecutionProvider
  mock: false
```

## Current Boundary

The inference engine returns raw output arrays and timing metadata. YOLO output parsing, non-max suppression, danger decisions, and STOP integration are reserved for later prompts.
