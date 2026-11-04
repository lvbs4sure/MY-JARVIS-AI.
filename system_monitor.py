"""Read-only local telemetry. No network requests, process inspection or elevation."""
from datetime import datetime
from pathlib import Path
import math
import platform
import shutil
import time

try:
    import psutil
except ImportError:
    psutil = None

SAFE_ERRORS = (OSError, RuntimeError, ValueError, TypeError, AttributeError, NotImplementedError)
if psutil is not None:
    SAFE_ERRORS += (psutil.Error,)


def percent(value):
    number = float(value)
    return number if math.isfinite(number) and 0 <= number <= 100 else None


def display_percent(value):
    return "N/A" if value is None else f"{value:.0f}%"


class SystemMonitor:
    def __init__(self, api=None, clock=time.monotonic):
        self.api = api if api is not None else psutil
        self.clock = clock
        self.previous_network = None

    def sample(self):
        result = {key: "N/A" for key in ("cpu", "ram", "disk", "battery", "network", "download", "upload", "temperature", "power", "disk_free", "ram_detail")}
        result.update(time=datetime.now().astimezone().strftime("%H:%M:%S"), platform=platform.system(), cpu_percent=None, ram_percent=None)
        api = self.api
        if api is not None:
            try:
                result["cpu_percent"] = percent(api.cpu_percent(interval=0.1))
                result["cpu"] = display_percent(result["cpu_percent"])
            except SAFE_ERRORS:
                pass
            try:
                ram = api.virtual_memory()
                result["ram_percent"] = percent(ram.percent)
                result["ram"] = display_percent(result["ram_percent"])
                result["ram_detail"] = f"{ram.used / 2**30:.1f} / {ram.total / 2**30:.1f} GiB"
            except SAFE_ERRORS:
                pass
            try:
                battery = api.sensors_battery()
                if battery is not None:
                    result["battery"] = display_percent(percent(battery.percent))
                    result["power"] = "Plugged in" if battery.power_plugged else "On battery"
            except SAFE_ERRORS:
                pass
            try:
                links = api.net_if_stats()
                active = any(link.isup for name, link in links.items() if "loopback" not in name.lower() and name.lower() != "lo")
                result["network"] = "Link up" if active else "Link down"
            except SAFE_ERRORS:
                pass
            try:
                counters = api.net_io_counters()
                now = self.clock()
                if counters is not None:
                    current = (now, counters.bytes_recv, counters.bytes_sent)
                    if self.previous_network is not None:
                        before, received, sent = self.previous_network
                        elapsed = now - before
                        if elapsed > 0 and counters.bytes_recv >= received and counters.bytes_sent >= sent:
                            result["download"] = f"{(counters.bytes_recv - received) / elapsed / 1024:.1f} KiB/s"
                            result["upload"] = f"{(counters.bytes_sent - sent) / elapsed / 1024:.1f} KiB/s"
                    self.previous_network = current
                else:
                    self.previous_network = None
            except SAFE_ERRORS:
                self.previous_network = None
            try:
                temperatures = api.sensors_temperatures()
                values = [entry.current for entries in temperatures.values() for entry in entries if entry.current is not None and 0 < entry.current < 150]
                if values:
                    result["temperature"] = f"{max(values):.0f} °C"
            except SAFE_ERRORS:
                pass
        try:
            drive = Path(__file__).resolve().anchor
            usage = shutil.disk_usage(drive)
            if usage.total:
                result["disk"] = display_percent(percent(usage.used / usage.total * 100))
                result["disk_free"] = f"{usage.free / 2**30:.1f} GiB free"
        except SAFE_ERRORS:
            pass
        return result


def snapshot():
    """One sample; use a persistent SystemMonitor for network-rate deltas."""
    return SystemMonitor().sample()
