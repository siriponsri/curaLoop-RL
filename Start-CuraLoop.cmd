@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
  ".venv\Scripts\python.exe" -m pip install -r requirements-lock.txt
  if errorlevel 1 goto :failed
  ".venv\Scripts\python.exe" -m pip install -e . --no-deps
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
if errorlevel 1 goto :failed
echo Open http://127.0.0.1:8501 in your browser. Press Ctrl+C to stop.
".venv\Scripts\python.exe" -m streamlit run app\streamlit_app.py
exit /b %errorlevel%
:failed
echo Setup failed. See README.md for the explicit PowerShell commands.
pause
exit /b 1
