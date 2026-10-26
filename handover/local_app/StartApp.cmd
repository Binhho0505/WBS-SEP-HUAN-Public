@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if errorlevel 1 (python -m venv .venv) else (py -3 -m venv .venv)
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import openpyxl; assert openpyxl.__version__ == '3.1.5'" >nul 2>nul
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install -r local_app\requirements.txt
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import anthropic" >nul 2>nul
if errorlevel 1 (
  echo Optional AI SDK: installing local_app\requirements-ai.txt. The estimate app still runs if this fails.
  ".venv\Scripts\python.exe" -m pip install -r local_app\requirements-ai.txt
)
echo Open http://127.0.0.1:8765 in your browser. Press Ctrl+C to stop.
".venv\Scripts\python.exe" -X utf8 local_app\server.py --port 8765
if errorlevel 1 goto failed
exit /b 0
:failed
echo App did not start. Read the error above. No port or policy is changed automatically.
pause
exit /b 1
