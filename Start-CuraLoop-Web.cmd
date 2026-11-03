@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\curaloop-web-ready.txt" (
  call Setup-CuraLoop-Web.cmd --no-pause
  if errorlevel 1 goto :failed
)
echo Starting the local web application. Press Ctrl+C in this window to stop.
".venv\Scripts\python.exe" scripts\start_web.py
if errorlevel 1 goto :failed
exit /b 0
:failed
echo CuraLoop-RL did not start. Read the error above and START_WINDOWS_TH.md.
pause
exit /b 1
