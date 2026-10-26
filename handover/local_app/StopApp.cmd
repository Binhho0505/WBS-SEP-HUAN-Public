@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo No local environment found. Stop the terminal running the app.
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 local_app\stop_app.py
if errorlevel 1 pause
