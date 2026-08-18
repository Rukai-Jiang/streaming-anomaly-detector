import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))

from anomaly_detector import RollingZScoreDetector


class RollingZScoreDetectorTests(unittest.TestCase):
    def test_detects_spike_after_baseline(self) -> None:
        detector = RollingZScoreDetector(
            window_size=5, min_samples=5, threshold=3
        )
        for value in [10.0, 10.2, 9.8, 10.1, 9.9]:
            self.assertFalse(detector.update(value).is_anomaly)

        detection = detector.update(15.0, timestamp="2026-08-18T10:00:00Z")
        self.assertTrue(detection.is_anomaly)
        self.assertGreater(detection.score, 3)
        self.assertEqual(detection.timestamp, "2026-08-18T10:00:00Z")

    def test_constant_baseline_handles_nonzero_deviation(self) -> None:
        detector = RollingZScoreDetector(
            window_size=3, min_samples=3, threshold=3
        )
        for _ in range(3):
            detector.update(5)

        detection = detector.update(6)
        self.assertTrue(detection.is_anomaly)
        self.assertTrue(math.isinf(detection.score))

    def test_window_rolls_forward(self) -> None:
        detector = RollingZScoreDetector(
            window_size=3, min_samples=3, threshold=100
        )
        for value in [1, 2, 3, 4]:
            detector.update(value)

        detection = detector.update(5)
        self.assertAlmostEqual(detection.baseline_mean or 0, 3.0)
        self.assertEqual(detection.baseline_samples, 3)

    def test_rejects_non_finite_input(self) -> None:
        detector = RollingZScoreDetector()
        with self.assertRaises(ValueError):
            detector.update(float("nan"))


if __name__ == "__main__":
    unittest.main()

