"""Tests for capture feedback thresholds."""

import unittest

from nightygo.audio import StoneCaptureSound


class CaptureSoundThresholdTests(unittest.TestCase):
    def test_group_sizes_select_distinct_capture_patterns(self) -> None:
        self.assertIsNone(StoneCaptureSound.band_for_count(0))
        self.assertEqual(StoneCaptureSound.band_for_count(1), "single")
        self.assertEqual(StoneCaptureSound.band_for_count(2), "small_group")
        self.assertEqual(StoneCaptureSound.band_for_count(3), "small_group")
        self.assertEqual(StoneCaptureSound.band_for_count(4), "group")
        self.assertEqual(StoneCaptureSound.band_for_count(7), "group")
        self.assertEqual(StoneCaptureSound.band_for_count(8), "large_group")
        self.assertEqual(StoneCaptureSound.band_for_count(40), "large_group")


if __name__ == "__main__":
    unittest.main()
