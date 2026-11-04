"""Approved isolated Ollama service. No installer, global env changes or secrets."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import socket
import subprocess
import time
from urllib import request

import psutil
from jarvis_ai import _local_urlopen
from local_ai import hardware_readiness

ROOT = Path(__file__).resolve().parent
MODEL = "qwen3:0.6b"
BASE = "http://127.0.0.1:11434"
MIN_RAM_GIB = 2.0


def paths(root=ROOT):
    root = Path(root).resolve()
    runtime = (root / ".local-ai").resolve()
    models = (root / ".local-models").resolve()
    if not runtime.is_relative_to(root) or not models.is_relative_to(root):
        raise RuntimeError("Local runtime paths must remain inside this JARVIS folder.")
    return runtime, models


def child_environment(root=ROOT, source=None):
    source = os.environ if source is None else source
    runtime, models = paths(root)
    profile = runtime / "profile"
    # Allowlist essential Windows variables; never inherit AI/provider credentials.
    env = {name: source[name] for name in ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE") if name in source}
    system = Path(env.get("SYSTEMROOT", r"C:\Windows"))
    env.update({
        "PATH": os.pathsep.join(map(str, (runtime / "runtime", runtime / "runtime" / "lib" / "ollama", system / "System32"))),
        "USERPROFILE": str(profile), "APPDATA": str(profile / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(profile / "AppData" / "Local"),
        "TEMP": str(profile / "Temp"), "TMP": str(profile / "Temp"),
        "OLLAMA_MODELS": str(models), "OLLAMA_HOST": "127.0.0.1:11434",
        "OLLAMA_NO_CLOUD": "1", "OLLAMA_CONTEXT_LENGTH": "2048",
        "OLLAMA_NUM_PARALLEL": "1", "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_KEEP_ALIVE": "0",
    })
    return env


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_executable(root=ROOT):
    runtime, _ = paths(root)
    executable = runtime / "runtime" / "ollama.exe"
    manifest = json.loads((runtime / "installation.json").read_text())
    if not executable.is_file() or sha256(executable) != manifest.get("executable_sha256"):
        raise RuntimeError("The isolated Ollama executable failed its recorded integrity check.")
    return executable


def owned_process(root=ROOT):
    runtime, _ = paths(root)
    try:
        state = json.loads((runtime / "service.json").read_text())
        process = psutil.Process(state["pid"])
        expected = (runtime / "runtime" / "ollama.exe").resolve()
        if Path(process.exe()).resolve() == expected and abs(process.create_time() - state["created"]) < 0.1:
            return process
    except (OSError, ValueError, KeyError, psutil.Error):
        pass
    return None


def port_open():
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=1):
            return True
    except OSError:
        return False


def get_json(endpoint):
    with _local_urlopen(BASE + endpoint, timeout=3) as response:
        return json.loads(response.read(1_000_000))


def start(root=ROOT):
    runtime, models = paths(root)
    if port_open():
        if owned_process(root) is None:
            raise RuntimeError("Port 11434 belongs to an unverified service; it was left untouched.")
        return {"status": "running", "version": get_json("/api/version").get("version")}
    executable = verified_executable(root)
    env = child_environment(root)
    for name in ("USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "OLLAMA_MODELS"):
        Path(env[name]).mkdir(parents=True, exist_ok=True)
    with (runtime / "server.log").open("ab") as log:
        child = subprocess.Popen([str(executable), "serve"], cwd=runtime, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    created = psutil.Process(child.pid).create_time()
    (runtime / "service.json").write_text(json.dumps({"pid": child.pid, "created": created}))
    for _ in range(60):
        if child.poll() is not None:
            raise RuntimeError("Isolated Ollama exited during startup. See its local server log.")
        try:
            version = get_json("/api/version").get("version")
            return {"status": "started", "version": version}
        except (OSError, ValueError):
            time.sleep(0.25)
    raise RuntimeError("Local Ollama did not become ready within the startup window.")


def pull(root=ROOT):
    start(root)
    runtime, _ = paths(root)
    payload = json.dumps({"model": MODEL, "stream": True}).encode()
    req = request.Request(BASE + "/api/pull", data=payload, headers={"Content-Type": "application/json"})
    last = 0
    with _local_urlopen(req, timeout=1800) as response:
        while line := response.readline(1_000_001):
            if len(line) > 1_000_000:
                raise RuntimeError("Oversized model-download status.")
            item = json.loads(line)
            if item.get("error"):
                safe_error = re.sub(r"https?://\S+", "<download endpoint>", str(item["error"]))[:1000]
                (runtime / "pull-error.json").write_text(json.dumps({"message": safe_error}))
                raise RuntimeError("The approved model download failed; see its local status.")
            (runtime / "pull-progress.json").write_text(json.dumps(item))
            if time.monotonic() - last > 10 or item.get("status") == "success":
                print(json.dumps({key: item[key] for key in ("status", "completed", "total") if key in item}), flush=True)
                last = time.monotonic()
    models = get_json("/api/tags").get("models", [])
    found = next((model for model in models if model.get("name") == MODEL), None)
    if not found:
        raise RuntimeError("The approved model is not listed after downloading.")
    receipt = {"model": MODEL, "digest": found.get("digest"), "size": found.get("size")}
    (runtime / "model-receipt.json").write_text(json.dumps(receipt))
    return {"status": "downloaded", **receipt}


def benchmark(root=ROOT):
    hardware = hardware_readiness()
    free = hardware.get("ram_available_gib")
    raw_bytes = hardware.get("ram_available_bytes")
    enough = raw_bytes >= MIN_RAM_GIB * 2**30 if isinstance(raw_bytes, int) else free is not None and free >= MIN_RAM_GIB
    if not enough:
        return {"status": "deferred", "reason": "At least 2 GiB free RAM is required for this baseline test.", "ram_available_gib": free}
    start(root)
    payload = {"model": MODEL, "stream": False, "think": False, "keep_alive": 0, "messages": [{"role": "user", "content": "Reply with exactly LOCAL_JARVIS_READY"}], "options": {"num_ctx": 1024, "num_predict": 32, "num_thread": 2}}
    req = request.Request(BASE + "/api/chat", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    began = time.monotonic()
    with _local_urlopen(req, timeout=90) as response:
        result = json.loads(response.read(1_000_000))
    answer = result.get("message", {}).get("content", "")
    receipt = {"status": "passed" if answer.strip() == "LOCAL_JARVIS_READY" else "failed", "seconds": round(time.monotonic() - began, 2), "model": MODEL, "ram_available_gib": free}
    runtime, _ = paths(root)
    (runtime / "benchmark.json").write_text(json.dumps(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description="Manage only this JARVIS folder's isolated Ollama")
    parser.add_argument("action", choices=["start", "pull", "benchmark", "status", "stop"])
    action = parser.parse_args().action
    if action == "start":
        result = start()
    elif action == "pull":
        result = pull()
    elif action == "benchmark":
        result = benchmark()
    elif action == "stop":
        process = owned_process()
        if process is None:
            raise RuntimeError("No verified isolated process to stop; other services were left untouched.")
        process.terminate()
        result = {"status": "stopped"}
    else:
        result = {"owned_process": owned_process() is not None, "reachable": port_open()}
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, psutil.Error) as exc:
        print("Isolated local AI: " + str(exc))
        raise SystemExit(1)
