@echo off
setlocal
cd /d "%~dp0"
title JARVIS - Personal AI
py -3 --version >nul 2>&1
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python is not installed or not on PATH.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PYTHON=python"
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating JARVIS private Python environment...
  %PYTHON% -m venv .venv
  if errorlevel 1 goto :failed
)
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created private .env configuration.
  echo To use your existing Gemini key, copy ONLY its GEMINI_API_KEY value
  echo into this new .env file, and set JARVIS_PROVIDER=gemini.
  echo Do not upload .env to GitHub.
)
echo Installing or updating JARVIS dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo Launching JARVIS at http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto :failed
exit /b 0
:failed
echo JARVIS could not start. Read the error above.
pause
exit /b 1
