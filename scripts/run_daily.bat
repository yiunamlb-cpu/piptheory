@echo off
rem nam-hedgefund daily bias engine run.
rem Registered with Windows Task Scheduler — see install instructions in
rem scripts/install_scheduled_task.ps1.
rem
rem This script:
rem   1. Sets working directory to the project root
rem   2. Activates Python via the project's venv (no shell activation needed)
rem   3. Runs the bias engine
rem   4. Appends stdout+stderr to logs/bias_engine.log with a timestamped header
rem
rem The dashboard reads bias_cards/{date}/ output, so once this finishes the
rem next time the dashboard auto-reruns it'll show the fresh brief.

setlocal

set REPO=C:\Users\user\Downloads\claude hedgefund
cd /d "%REPO%"

set PYTHONPATH=%REPO%
set PYTHONIOENCODING=utf-8

if not exist "logs" mkdir logs

echo. >> "logs\bias_engine.log"
echo ================================================================ >> "logs\bias_engine.log"
echo Run started %DATE% %TIME% >> "logs\bias_engine.log"
echo ================================================================ >> "logs\bias_engine.log"

".venv\Scripts\python.exe" "scripts\run_bias_engine.py" 1>> "logs\bias_engine.log" 2>&1

echo. >> "logs\bias_engine.log"
echo Run finished %DATE% %TIME% (exit %ERRORLEVEL%) >> "logs\bias_engine.log"

endlocal
