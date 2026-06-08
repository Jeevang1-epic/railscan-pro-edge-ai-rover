# Demo Script

Use this as a 2-3 minute presentation guide.

## Opening

RailScan Pro is a proof-of-concept edge-AI railway track inspection rover. The goal is to demonstrate how a low-cost rover could inspect visible rail defects or obstructions and trigger a safety response.

## Problem

Manual inspection is slow, repetitive, and difficult to scale. RailScan Pro focuses on a practical MVP: visible defect detection and a clear emergency-stop path.

## Solution

The project uses split logic:

- Python/local PC handles camera frames, inference, detection postprocessing, decision logic, and runtime reporting.
- Arduino UNO handles motor control and the latched STOP behavior.

This split keeps safety-critical motor cutoff logic on the microcontroller while allowing the Python side to evolve.

## Safe Runtime Demo

First run the safe no-defect demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 5
```

Then run the simulated defect demo:

```bash
python scripts/run_demo.py --synthetic --mock-inference --serial-dry-run --frames 6 --simulate-defect-frame 3
```

Point out:

- the run is finite
- inference is mock mode
- the defect is simulated
- STOP is dry-run only
- the runtime summary is written to `runs/reports/runtime_summary.json`

## Why Dry-Run Matters

The project intentionally blocks accidental hardware actions. Real STOP requires both `--enable-real-stop` and `--confirm-wheels-lifted`, and hardware validation is pending until the rover is physically prepared.

## What Remains

Next steps are:

- collect and label real rail/track images
- train and export a real ONNX model
- validate real camera capture
- validate Arduino STOP with wheels lifted
- run final hardware demo only after safety checks pass
