# Camera Capture Setup

Prompt 3 adds the camera capture foundation only. It does not run AI inference and does not trigger serial STOP from frames.

## Synthetic Validation

Use synthetic mode when no webcam is available:

```bash
python scripts/camera_test.py --synthetic --frames 5
```

Synthetic mode generates NumPy frames with the configured shape and does not open camera hardware.

## Real Camera Validation

Only run this when a webcam or USB camera is connected:

```bash
python scripts/camera_test.py --source 0 --frames 30
```

Use a different source if needed, such as another camera index, video file path, or stream URL.

Display is optional:

```bash
python scripts/camera_test.py --source 0 --frames 100 --display
```

Do not enable display mode in headless validation.

## Configuration

Camera defaults live in `config/railscan.yaml`:

```yaml
camera:
  source: 0
  width: 640
  height: 480
  model_input_size: 320
  synthetic: false
```

The camera module reports frame index, timestamp, frame shape, and approximate observed FPS.

## Current Boundary

Prompt 3 is camera-only. AI inference, defect decisions, and serial STOP integration are reserved for later prompts.
