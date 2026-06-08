# Detection Adapter

Prompt 6 adds a pure postprocessing layer between raw ONNX model outputs and the decision engine.

```text
raw YOLO-like output -> parsed candidates -> NMS -> Detection objects
```

This layer does not open cameras, load ONNX models, call serial STOP, or control hardware.

## Supported Output Shapes

The adapter supports one or more numeric output arrays with these first-pass shapes:

```text
(1, N, 4 + C)
(1, 4 + C, N)
(N, 4 + C)
```

When `postprocessing.has_objectness` is `true`, each row must be:

```text
cx, cy, w, h, objectness, class_score_0, class_score_1, ...
```

When `postprocessing.has_objectness` is `false`, each row must be:

```text
cx, cy, w, h, class_score_0, class_score_1, ...
```

The class-score count must match `model.class_names`.

## Box Format

Prompt 6 supports `postprocessing.input_box_format: "cxcywh"` only.

The adapter converts boxes into decision-layer `bbox` values:

```text
x1, y1, x2, y2
```

Coordinates are passed through in the same scale as the model output. If the model emits normalized coordinates, the returned boxes are normalized. If the model emits pixel coordinates, the returned boxes are pixel coordinates.

## Confidence And NMS

- Without objectness, confidence is the highest class score.
- With objectness, confidence is `objectness * highest_class_score`.
- Candidates below `model.confidence_threshold` are filtered out.
- NMS is class-aware, so overlapping boxes from different classes are kept.
- Returned detections are capped by `postprocessing.max_detections`.

## Validation

Run the deterministic adapter check:

```bash
python scripts/detection_test.py
```

Run the full no-hardware validation matrix from the README before moving to the next prompt.

## Current Limitations

- No YOLO model training or export is included.
- No model-specific output decoding beyond the documented layouts is included.
- No segmentation masks, keypoints, rotated boxes, or multi-head model outputs are interpreted.
- No decision or serial STOP integration happens in this layer.
