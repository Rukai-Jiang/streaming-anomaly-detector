from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path

from .detector import RollingZScoreDetector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect point anomalies in a timestamp,value CSV stream."
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--threshold", type=float, default=3.0)
    parser.add_argument("--min-samples", type=int)
    parser.add_argument("--all", action="store_true", help="emit every detection")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    detector = RollingZScoreDetector(
        window_size=args.window,
        threshold=args.threshold,
        min_samples=args.min_samples,
    )

    with args.csv_file.open(newline="", encoding="utf-8") as input_file:
        for row in csv.DictReader(input_file):
            detection = detector.update(float(row["value"]), row.get("timestamp"))
            if args.all or detection.is_anomaly:
                output = asdict(detection)
                if math.isinf(output["score"]):
                    output["score"] = "Infinity"
                print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()

