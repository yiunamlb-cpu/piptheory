# Register the dashboard watchdog as a Windows scheduled task.
# Runs every 2 minutes. Checks port 8501; relaunches uvicorn if dead.
#
# To install: open elevated PowerShell, then:
#   .\scripts\install_watchdog_task.ps1
#
# To remove:
#   Unregister-ScheduledTask -TaskName "NamHedgefund-Watchdog" -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName = "NamHedgefund-Watchdog"
$repo = "C:\Users\user\Downloads\claude hedgefund"
$watchdog = Join-Path $repo "scripts\dashboard_watchdog.vbs"

if (-not (Test-Path $watchdog)) {
    Write-Error "Watchdog script not found: $watchdog"
    exit 1
}

# Remove any existing version so install is idempotent
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Launch the watchdog directly via wscript.exe. wscript is genuinely
# windowless from the kernel's perspective — no console process is ever
# created — so this never flashes a window on the scheduler tick.
#
# Previous attempts:
#   v1 (628c5d6): powershell.exe -WindowStyle Hidden — flashed because
#     PowerShell creates a console before the hide flag takes effect.
#   v2 (27a702e): wscript run_hidden.vbs that exec'd powershell —
#     still flashed because the .vbs spawned PowerShell which is itself
#     a console app.
#   v3 (this):    pure VBScript, no PowerShell anywhere in the chain.
#     Watchdog logic ported to .vbs (HTTP health check via MSXML2,
#     hidden Run via WshShell). Truly silent.
$action = New-ScheduledTaskAction `
    -Execute "wscript.exe" `
    -Argument "`"$watchdog`""

# Repeat every 2 minutes, indefinitely. Start time is now (so it runs
# immediately after registration). Trigger needs a duration; using 9999
# days as effectively-forever per Microsoft's documented pattern.
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 2) `
    -RepetitionDuration (New-TimeSpan -Days 9999)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

# Run as the current user, with the user's environment, no admin needed —
# the .bat script doesn't require elevation.
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Watchdog for nam-hedgefund dashboard. Checks port 8501 every 2 minutes; relaunches uvicorn via run_dashboard.bat if dead."

Write-Host "Installed scheduled task: $taskName" -ForegroundColor Green
Write-Host "  Runs every 2 minutes."
Write-Host "  Logs to logs\watchdog.log when it has to act (silent when healthy)."
Write-Host ""
Write-Host "To verify: Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
Write-Host "To remove: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
