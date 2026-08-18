# Streaming Anomaly Detector

A dependency-free Python detector for finding point anomalies in live metric streams. It compares each incoming value with a rolling baseline and updates window statistics in constant time.

## Why this project

Monitoring systems need to process telemetry continuously without storing an entire history. This project demonstrates online algorithms, numerical edge-case handling, a reusable Python API, and a JSON-lines command-line interface.

## Features

- O(1) processing per sample
- Fixed-memory rolling window
- Configurable z-score threshold and warm-up period
- Stable handling of constant baselines
- Structured detection results
- CSV input and JSON-lines output
- Dependency-free test suite

## Quick start

```bash
PYTHONPATH=src python3 -m anomaly_detector.cli examples/metrics.csv \  --window 5 --min-samples 5 --threshold 3
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Algorithm

The detector keeps a deque plus the rolling sum and sum of squares. Mean and population variance are available without rescanning the window. A new value is scored against the existing baseline before insertion, so an anomaly cannot weaken its own score.
