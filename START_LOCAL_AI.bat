@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Start the new JARVIS once to prepare its private Python environment.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" local_runtime.py start
if errorlevel 1 (
  echo The isolated local service could not start. No other service was changed.
  pause
  exit /b 1
)
exit /b 0
