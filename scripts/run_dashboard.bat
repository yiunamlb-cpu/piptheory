@echo off
rem nam-hedgefund dashboard auto-start.
rem Registered with Windows Task Scheduler — see scripts/install_dashboard_task.ps1.
rem
rem This script:
rem   1. Sets working directory to the project root
rem   2. Activates Python via the project's venv (no shell activation needed)
rem   3. Starts Streamlit in headless mode bound to all interfaces (Tailscale-reachable)
rem   4. Logs to logs/dashboard.log
rem
rem Streamlit Serve is also re-applied so the https://desktop.tail*.ts.net/
rem URL re-attaches after a reboot.

setlocal

set REPO=C:\Users\user\Downloads\claude hedgefund
cd /d "%REPO%"

set PYTHONPATH=%REPO%
set PYTHONIOENCODING=utf-8

if not exist "logs" mkdir logs

echo. >> "logs\dashboard.log"
echo ================================================================ >> "logs\dashboard.log"
echo Dashboard started %DATE% %TIME% >> "logs\dashboard.log"
echo ================================================================ >> "logs\dashboard.log"

rem Re-apply Tailscale Serve mapping in case it didn't persist across reboot.
"C:\Program Files\Tailscale\tailscale.exe" serve --bg http://localhost:8501 1>> "logs\dashboard.log" 2>&1

rem Start Streamlit in the background. The cmd /c start technique detaches
rem so the scheduled task doesn't sit around as a parent process.
start "" /B ".venv\Scripts\python.exe" -m streamlit run "dashboard\app.py" 1>> "logs\dashboard.log" 2>&1

endlocal
