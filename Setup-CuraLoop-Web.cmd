@echo off
setlocal
cd /d "%~dp0"
echo CuraLoop-RL Web - first-time local setup
if exist ".venv\Scripts\python.exe" goto :install
where py >nul 2>&1
if errorlevel 1 goto :python_fallback
py -3.11 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  py -3.11 -m venv .venv
  goto :venv_result
)
py -3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  py -3.12 -m venv .venv
  goto :venv_result
)
py -3 -m venv .venv
goto :venv_result
:python_fallback
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.11 or 3.12 is required. Install the official 64-bit Python for your user account.
  goto :failed
)
python -m venv .venv
:venv_result
if errorlevel 1 goto :failed
:install
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements-web-lock.txt
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -e ".[web]" --no-deps
if errorlevel 1 goto :failed
if not exist "frontend\dist\index.html" (
  where npm >nul 2>&1
  if errorlevel 1 (
    echo Built frontend is missing. Install Node.js 22.12+ or use the complete release ZIP.
    goto :failed
  )
  pushd frontend
  call npm ci
  if errorlevel 1 (
    popd
    goto :failed
  )
  call npm run build
  if errorlevel 1 (
    popd
    goto :failed
  )
  popd
)
".venv\Scripts\python.exe" scripts\start_web.py --check
if errorlevel 1 goto :failed
echo 0.3.0>".venv\curaloop-web-ready.txt"
echo Setup complete. Start-CuraLoop-Web.cmd runs offline at http://127.0.0.1:8000
exit /b 0
:failed
echo Setup could not complete. See START_WINDOWS.md for manual recovery commands.
if /I not "%~1"=="--no-pause" pause
exit /b 1
