# RailScan V1 Dataset Template

This folder is the YOLO detection dataset template for RailScan Pro.

Expected layout:

```text
datasets/railscan_v1/
|-- data.yaml
|-- images/
|   |-- train/
|   |-- val/
|   `-- test/
`-- labels/
    |-- train/
    |-- val/
    `-- test/
```

YOLO detection labels use one text file per image. Each line is:

```text
class_id x_center y_center width height
```

All box coordinates are normalized from `0.0` to `1.0` relative to the image width and height.

Class order:

```text
0 visible_crack
1 surface_damage
2 missing_fastener
3 foreign_object
4 unsafe_track_region
```

The dataset YAML declares `nc: 5`; keep that value aligned with the class list.

Do not commit large datasets unless that is intentional for the project. For normal development, keep only this template or a very small labeled sample set in Git, and store larger datasets outside the repository.

Record dataset size, source notes, and labeling status in `docs/demo-report-template.md` before claiming any real model-training result.
