from types import SimpleNamespace as NS
import unittest
from unittest.mock import MagicMock, patch

import system_monitor
from system_monitor import SystemMonitor


class SystemMonitorTests(unittest.TestCase):
    def api(self):
        api = MagicMock()
        api.cpu_percent.return_value = 37.5
        api.virtual_memory.return_value = NS(percent=62, used=5 * 2**30, total=8 * 2**30)
        api.sensors_battery.return_value = NS(percent=81, power_plugged=True)
        api.net_if_stats.return_value = {"Wi-Fi": NS(isup=True), "Loopback": NS(isup=True)}
        api.net_io_counters.return_value = NS(bytes_recv=1024, bytes_sent=1024)
        api.sensors_temperatures.return_value = {}
        return api

    def test_real_fields_units_and_bounded_cpu_sample(self):
        api = self.api()
        with patch("system_monitor.shutil.disk_usage", return_value=NS(total=100 * 2**30, used=40 * 2**30, free=60 * 2**30)):
            sample = SystemMonitor(api).sample()
        self.assertEqual(sample["cpu"], "38%")
        self.assertEqual(sample["ram"], "62%")
        self.assertEqual(sample["disk"], "40%")
        self.assertEqual(sample["disk_free"], "60.0 GiB free")
        self.assertEqual(sample["battery"], "81%")
        self.assertEqual(sample["network"], "Link up")
        self.assertEqual(sample["temperature"], "N/A")
        api.cpu_percent.assert_called_once_with(interval=0.1)

    def test_rates_require_two_samples_and_use_elapsed_time(self):
        api = self.api()
        api.net_io_counters.side_effect = [NS(bytes_recv=1000, bytes_sent=2000), NS(bytes_recv=5096, bytes_sent=4048)]
        monitor = SystemMonitor(api, clock=iter([10, 12]).__next__)
        self.assertEqual(monitor.sample()["download"], "N/A")
        sample = monitor.sample()
        self.assertEqual(sample["download"], "2.0 KiB/s")
        self.assertEqual(sample["upload"], "1.0 KiB/s")

    def test_counter_reset_never_produces_negative_rate(self):
        api = self.api()
        api.net_io_counters.side_effect = [NS(bytes_recv=5000, bytes_sent=5000), NS(bytes_recv=10, bytes_sent=10)]
        monitor = SystemMonitor(api, clock=iter([1, 3]).__next__)
        monitor.sample()
        self.assertEqual(monitor.sample()["upload"], "N/A")

    def test_failed_sample_breaks_rate_baseline(self):
        api = self.api()
        api.net_io_counters.side_effect = [NS(bytes_recv=1000, bytes_sent=1000), OSError(), NS(bytes_recv=9000, bytes_sent=9000)]
        monitor = SystemMonitor(api, clock=iter([1, 5]).__next__)
        monitor.sample()
        self.assertEqual(monitor.sample()["download"], "N/A")
        self.assertEqual(monitor.sample()["download"], "N/A")

    def test_missing_battery_temperature_and_link_do_not_fake_values(self):
        api = self.api()
        api.sensors_battery.return_value = None
        api.sensors_temperatures.side_effect = AttributeError()
        api.net_if_stats.return_value = {"Loopback": NS(isup=True), "Wi-Fi": NS(isup=False)}
        sample = SystemMonitor(api).sample()
        self.assertEqual(sample["battery"], "N/A")
        self.assertEqual(sample["temperature"], "N/A")
        self.assertEqual(sample["network"], "Link down")

    def test_sensor_failure_does_not_hide_other_readings(self):
        api = self.api()
        api.cpu_percent.side_effect = OSError()
        api.sensors_temperatures.return_value = {"package": [NS(current=54.1)]}
        sample = SystemMonitor(api).sample()
        self.assertEqual(sample["cpu"], "N/A")
        self.assertEqual(sample["ram"], "62%")
        self.assertEqual(sample["temperature"], "54 °C")

    def test_invalid_cpu_number_remains_unavailable(self):
        api = self.api()
        api.cpu_percent.return_value = float("nan")
        self.assertIsNone(SystemMonitor(api).sample()["cpu_percent"])


class SnapshotContractTests(unittest.TestCase):
    def test_snapshot_has_expected_string_fields(self):
        result = system_monitor.snapshot()
        for key in ("time", "platform", "cpu", "ram", "disk", "battery", "network"):
            self.assertIn(key, result)
            self.assertIsInstance(result[key], str)
        self.assertIn(result["network"], ("N/A", "Link up", "Link down"))

    def test_disk_failure_is_reported_as_unavailable(self):
        with patch.object(system_monitor.shutil, "disk_usage", side_effect=OSError("unavailable")):
            self.assertEqual(system_monitor.snapshot()["disk"], "N/A")

    def test_disk_zero_total_is_unavailable(self):
        with patch.object(system_monitor.shutil, "disk_usage", return_value=NS(total=0, used=0, free=0)):
            self.assertEqual(system_monitor.snapshot()["disk"], "N/A")

    def test_disk_percentage_uses_measured_usage(self):
        with patch.object(system_monitor.shutil, "disk_usage", return_value=NS(total=100, used=25, free=75)):
            self.assertEqual(system_monitor.snapshot()["disk"], "25%")
