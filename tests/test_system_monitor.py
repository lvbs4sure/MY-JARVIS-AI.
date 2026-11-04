"""Regression tests for read-only, truthful system telemetry."""
import unittest
from unittest.mock import patch

import system_monitor


class SystemMonitorTests(unittest.TestCase):
    def test_snapshot_has_expected_string_fields(self):
        result = system_monitor.snapshot()
        for key in ("time", "platform", "cpu", "ram", "disk", "battery", "network"):
            self.assertIn(key, result)
            self.assertIsInstance(result[key], str)
        self.assertEqual(result["network"], "N/A")

    def test_disk_failure_is_reported_as_unavailable(self):
        with patch.object(system_monitor.shutil, "disk_usage", side_effect=OSError("unavailable")):
            self.assertEqual(system_monitor.snapshot()["disk"], "N/A")

    def test_disk_zero_total_is_unavailable(self):
        with patch.object(system_monitor.shutil, "disk_usage", return_value=(0, 0, 0)):
            self.assertEqual(system_monitor.snapshot()["disk"], "N/A")

    def test_disk_percentage_uses_measured_usage(self):
        with patch.object(system_monitor.shutil, "disk_usage", return_value=(100, 25, 75)):
            self.assertEqual(system_monitor.snapshot()["disk"], "25%")


if __name__ == "__main__":
    unittest.main()
