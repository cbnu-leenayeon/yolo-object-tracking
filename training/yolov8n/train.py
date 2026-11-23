"""Replay the recorded local training configuration; assembled during cleanup.

The original training entry command was not saved. args.original.yaml and
train_args.checkpoint.json preserve the actual recorded settings.
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="0")
    args = parser.parse_args()
    from ultralytics import YOLO

    root = Path(__file__).resolve().parents[2]
    saved = json.loads((Path(__file__).parent / "train_args.checkpoint.json").read_text("utf-8"))
    options = {key: saved[key] for key in (
        "epochs", "patience", "batch", "imgsz", "optimizer", "lr0", "lrf",
        "momentum", "weight_decay", "warmup_epochs", "warmup_momentum",
        "warmup_bias_lr", "seed", "deterministic", "workers", "amp",
        "close_mosaic", "hsv_h", "hsv_s", "hsv_v", "degrees", "translate",
        "scale", "shear", "perspective", "flipud", "fliplr", "mosaic",
        "mixup", "copy_paste") if key in saved}
    model = YOLO(str(root / "training/yolov8n/yolov8n.pt"))
    model.train(data=str(root / "datasets/yolov8n/data.yaml"),
                project=str(root / "runs/detect"), name="yolov8n_reproduction",
                device=args.device, exist_ok=False, **options)


if __name__ == "__main__":
    main()
