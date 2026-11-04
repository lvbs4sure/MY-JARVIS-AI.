"""Safe, read-only command-centre system overview.

Telemetry is never fabricated: unavailable values remain N/A.
"""
from datetime import datetime
import os
import platform
import shutil


def snapshot():
    result = {
        "time": datetime.now().astimezone().strftime("%H:%M:%S"),
        "platform": platform.system(),
        "cpu": "N/A",
        "ram": "N/A",
        "disk": "N/A",
        "battery": "N/A",
        "network": "N/A",
    }
    try:
        import psutil
    except ImportError:
        psutil = None
    if psutil is not None:
        try:
            result["cpu"] = f"{psutil.cpu_percent(interval=None):.0f}%"
        except (OSError, RuntimeError, ValueError):
            pass
        try:
            result["ram"] = f"{psutil.virtual_memory().percent:.0f}%"
        except (OSError, RuntimeError, ValueError):
            pass
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                result["battery"] = f"{battery.percent:.0f}%"
        except (OSError, RuntimeError, ValueError, AttributeError):
            pass
    try:
        drive = os.path.splitdrive(os.path.abspath(__file__))[0] + os.sep if os.name == "nt" else "/"
        usage = shutil.disk_usage(drive)
        result["disk"] = f"{(usage.used / usage.total) * 100:.0f}%" if usage.total else "N/A"
    except (OSError, ValueError, ZeroDivisionError):
        pass
    return result
