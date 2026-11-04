@echo off
setlocal
cd /d "%~dp0"
title JARVIS - Personal AI
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" start_jarvis.py %*
  goto :done
)
py -3.13 --version >nul 2>&1
if not errorlevel 1 (
  py -3.13 start_jarvis.py %*
  goto :done
)
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
  "%LocalAppData%\Programs\Python\Python313\python.exe" start_jarvis.py %*
  goto :done
)
py -3 --version >nul 2>&1
if not errorlevel 1 (
  py -3 start_jarvis.py %*
  goto :done
)
python start_jarvis.py %*
:done
if errorlevel 1 (
  echo JARVIS could not start. Read the message above.
  pause
  exit /b 1
)
exit /b 0
