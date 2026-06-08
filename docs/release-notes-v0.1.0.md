# RailScan Pro v0.1.0 Release Notes

RailScan Pro v0.1.0 is the first submission-ready proof-of-concept release for a safe software demo and repository review.

## Version Summary

This release packages the current rover software foundation for Makers Conclave 2026 review. It demonstrates the architecture, safe runtime path, dry-run emergency STOP behavior, documentation, and validation evidence without requiring physical hardware.

## Completed Layers

- Repository foundation, config loading, logging, and custom exceptions
- Arduino UNO L298N motor STOP firmware with latched emergency stop
- Python serial STOP client with dry-run support
- OpenCV camera foundation with synthetic mode
- ONNX inference foundation with mock mode
- YOLO-like detection adapter
- Pure decision engine with smoothing and latch behavior
- YOLO dataset template plus dry-run training/export scripts
- Safe finite runtime pipeline
- Final QA checklist and demo runbooks
- Release/submission packaging manifest

## Safe Demo Commands

```bash
python scripts/final_qa.py
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
python scripts/package_demo_artifacts.py
```

These commands do not require a camera, Arduino, serial port, ONNX model, GPU, or training dependencies.

## Validation Status

The release validation matrix covers smoke checks, final QA, safe runtime demos, dry-run serial STOP, synthetic camera capture, mock inference, detection and decision tests, training/export dry-runs, unit tests, compile checks, and STOP safety scans.

Real camera, real ONNX model, real serial hardware, and real training/export validations are pending until the matching hardware, dataset, and model artifacts are available.

## Known Limitations

- No trained model weights are committed.
- No real dataset images are committed.
- Real camera validation has not been claimed.
- Real Arduino serial STOP validation has not been claimed.
- Real ONNX inference validation has not been claimed.
- This proof-of-concept is not safety-certified for railway operation.

## Next Real-World Validation Steps

1. Collect and label a small real dataset using the class order in `datasets/railscan_v1/data.yaml`.
2. Train and export a real ONNX model.
3. Validate the model artifact with `scripts/validate_model_artifact.py`.
4. Validate camera capture with real hardware.
5. Upload Arduino firmware and run STOP validation with rover wheels lifted.
6. Record all real validation results in `docs/demo-report-template.md`.
