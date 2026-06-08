# Decision Engine

Prompt 5 adds the pure decision layer. It decides whether detections require a stop, but it does not send serial commands and does not control hardware.

## Inputs

The decision engine accepts normalized `Detection` objects:

```python
Detection(class_name="visible_crack", confidence=0.82)
```

Classes must already be named and confidence values must be normalized from `0.0` to `1.0`.

## Rules

1. Ignore classes not listed in `model.danger_classes`.
2. Ignore detections below `model.confidence_threshold`.
3. Immediately latch stop for danger detections at or above `model.high_confidence_threshold`.
4. If smoothing is enabled, latch stop when danger appears in `decision.required_hits` frames within the last `decision.window_size` frames.
5. Once latched, keep returning `should_stop=True` until `reset()` is called.

## Validation

Run the deterministic decision examples:

```bash
python scripts/decision_test.py
```

Run the full no-hardware test suite:

```bash
python -m pytest
```

## Current Boundary

This layer returns `DecisionResult`. It does not call `send_stop()`, open a camera, run a model, parse YOLO outputs, or run the full demo loop. Integration is reserved for later prompts.

## Safety Invariants

- The decision module is pure logic: detections in, decision result out.
- Confidence thresholds are inclusive at their boundaries.
- The smoothing window is bounded by `decision.window_size`.
- `reset()` clears both the latch and smoothing history.
- Non-danger detections and low-confidence danger detections do not count as smoothing hits.
