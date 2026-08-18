"""Streaming anomaly detection with constant-memory rolling statistics."""

from .detector import Detection, RollingZScoreDetector

__all__ = ["Detection", "RollingZScoreDetector"]

