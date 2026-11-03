@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto :setup
if not exist ".venv\curaloop-web-ready.txt" goto :setup
findstr /x /c:"0.3.0" ".venv\curaloop-web-ready.txt" >nul
if errorlevel 1 goto :setup
goto :start
:setup
call Setup-CuraLoop-Web.cmd --no-pause
if errorlevel 1 goto :failed
:start
echo Starting the local web application. Press Ctrl+C in this window to stop.
".venv\Scripts\python.exe" scripts\start_web.py %*
if errorlevel 1 goto :failed
exit /b 0
:failed
echo CuraLoop-RL did not start. Read the error above and START_WINDOWS.md.
pause
exit /b 1
