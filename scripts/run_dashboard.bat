@echo off
rem nam-hedgefund dashboard auto-start.
rem Registered with Windows Task Scheduler — see scripts/install_dashboard_task.ps1.
rem
rem Replaces the Streamlit launcher with FastAPI (uvicorn). Same port (8501),
rem same Tailscale Serve mapping, custom HTML/CSS, no framework UI surprises.

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

rem Re-apply Tailscale Serve mapping (idempotent; safe to call repeatedly).
"C:\Program Files\Tailscale\tailscale.exe" serve --bg http://localhost:8501 1>> "logs\dashboard.log" 2>&1

rem Start uvicorn in the background, bound to all interfaces on 8501.
start "" /B ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8501 --log-level info 1>> "logs\dashboard.log" 2>&1

endlocal
