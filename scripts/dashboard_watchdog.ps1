# nam-hedgefund dashboard watchdog.
# Runs on a schedule (every ~2 minutes). Checks whether port 8501 is
# listening locally; if not, launches scripts/run_dashboard.bat. Logs to
# logs/watchdog.log so transient failures leave a trail.
#
# Registered via scripts/install_watchdog_task.ps1.
#
# Why this exists: scripts/run_dashboard.bat runs at user logon only.
# If uvicorn dies mid-session (crash, forced restart for code update,
# OOM, machine sleep), the dashboard stays down until you next log out
# and back in. The Tailscale Serve mapping continues pointing at port
# 8501 with nothing listening, so mobile access silently breaks.
# Watchdog brings it back within a 2-minute window without intervention.

$ErrorActionPreference = "Continue"
$repo = "C:\Users\user\Downloads\claude hedgefund"
$port = 8501
$logFile = Join-Path $repo "logs\watchdog.log"

function Write-WdLog([string]$msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$ts $msg" -Encoding UTF8
}

# Make sure the logs dir exists (first run after a checkout)
$logsDir = Join-Path $repo "logs"
if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory | Out-Null }

# Is something listening on port 8501?
$listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    # Healthy — no action. Don't spam the log on every tick.
    exit 0
}

Write-WdLog "Dashboard down (no listener on $port). Launching run_dashboard.bat..."

# Launch detached so the watchdog task can exit immediately.
$bat = Join-Path $repo "scripts\run_dashboard.bat"
if (-not (Test-Path $bat)) {
    Write-WdLog "FATAL: $bat not found"
    exit 1
}
try {
    # -WindowStyle Hidden alone isn't enough for cmd.exe (.bat) — the
    # console host can flash for a moment before the hidden flag is
    # honoured. Wrapping with cmd.exe /c and /min plus -WindowStyle Hidden
    # combined cuts the visible flash to effectively nothing.
    Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "`"$bat`"" `
        -WindowStyle Hidden `
        -WorkingDirectory $repo
    Write-WdLog "Launched. Subsequent ticks will verify."
} catch {
    Write-WdLog "FAILED to start: $($_.Exception.Message)"
    exit 1
}

exit 0
