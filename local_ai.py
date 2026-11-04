"""Local-runtime discovery sends no prompts, memories or credentials."""
import json
import os
from pathlib import Path
import shutil

from jarvis_ai import _local_urlopen


def inspect_local_ai():
    endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    if endpoint not in ("http://127.0.0.1:11434", "http://localhost:11434"):
        return {"status": "invalid_configuration", "models": [], "message": "Local AI discovery only accepts localhost port 11434."}
    try:
        with _local_urlopen(endpoint + "/api/tags", timeout=3) as response:
            payload = response.read(1_000_001)
        if len(payload) > 1_000_000:
            raise ValueError("Response too large")
        data = json.loads(payload)
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise ValueError("Invalid model list")
        names = sorted({row["name"] for row in data["models"] if isinstance(row, dict) and isinstance(row.get("name"), str) and 0 < len(row["name"].strip()) <= 200})[:100]
        message = "Installed local models discovered." if names else "Ollama is running but has no installed models."
        return {"status": "available", "models": names, "message": message}
    except (ValueError, TypeError, UnicodeError):
        return {"status": "invalid_response", "models": [], "message": "The local runtime returned an unreadable model list."}
    except OSError:
        return {"status": "unavailable", "models": [], "message": "Ollama is not reachable on this laptop. No provider setting was changed."}


def hardware_readiness():
    result = {"ram_total_gib": None, "ram_available_gib": None, "disk_free_gib": None}
    try:
        import psutil
        memory = psutil.virtual_memory()
        result.update(ram_total_gib=round(memory.total / 2**30, 1), ram_available_gib=round(memory.available / 2**30, 1))
    except (ImportError, OSError, RuntimeError, ValueError):
        pass
    try:
        result["disk_free_gib"] = round(shutil.disk_usage(Path(__file__).resolve().anchor).free / 2**30, 1)
    except OSError:
        pass
    free = result["ram_available_gib"]
    result["advice"] = "Free RAM is low. Keep the working provider active until there is room to test a small local model." if free is not None and free < 2 else "Benchmark an installed model before making it the default. No model or software is downloaded by this check."
    return result
