"""Start this isolated installation without touching another JARVIS copy."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
from urllib import request, error
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8501"


def prepare(root=ROOT):
    root = Path(root)
    python = root / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        if sys.version_info < (3, 11):
            raise RuntimeError("Install Python 3.11 or newer, then start JARVIS again.")
        venv.EnvBuilder(with_pip=True).create(root / ".venv")
    requirements = root / "requirements.txt"
    signature = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = root / ".venv" / "jarvis-requirements.sha256"
    if not marker.exists() or marker.read_text().strip() != signature:
        command = [str(python), "-m", "pip", "install", "-r", str(requirements)]
        installed = subprocess.run(command + ["--no-index"], cwd=root).returncode == 0
        if not installed:
            subprocess.run(command, cwd=root, check=True)
        marker.write_text(signature, encoding="utf-8")
    configuration = root / ".env"
    if not configuration.exists():
        configuration.write_bytes((root / ".env.example").read_bytes())
    return python


def is_running():
    try:
        with request.build_opener(request.ProxyHandler({})).open(URL + "/_stcore/health", timeout=2) as response:
            return response.status == 200 and response.read(16).strip() == b"ok"
    except (OSError, error.URLError):
        return False


def main():
    parser = argparse.ArgumentParser(description="Start the new local JARVIS")
    parser.add_argument("--check", action="store_true", help="Prepare dependencies and configuration without launching")
    args = parser.parse_args()
    if not args.check and is_running():
        print("JARVIS is already running at " + URL)
        webbrowser.open(URL)
        return 0
    python = prepare()
    if args.check:
        print("JARVIS environment ready. Private configuration preserved.")
        return 0
    print("Opening JARVIS at " + URL + ". Keep this window open; press Ctrl+C to stop.")
    return subprocess.call([
        str(python), "-m", "streamlit", "run", str(ROOT / "app.py"),
        "--server.address=127.0.0.1", "--server.port=8501",
        "--server.headless=false", "--browser.gatherUsageStats=false",
    ], cwd=ROOT)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("JARVIS could not start: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
