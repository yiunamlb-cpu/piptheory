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
$script = Join-Path $repo "scripts\dashboard_watchdog.ps1"

if (-not (Test-Path $script)) {
    Write-Error "Watchdog script not found: $script"
    exit 1
}

# Remove any existing version so install is idempotent
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""

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
