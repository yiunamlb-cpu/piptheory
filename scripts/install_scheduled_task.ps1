# Registers the daily bias-engine run with Windows Task Scheduler.
#
# Default schedule: every day at 06:00 local time.
# Runs only when the user is logged on (no password prompt required).
# If the laptop is asleep or off at 06:00, the task does NOT fire that day —
# Windows Task Scheduler will catch up the next time the user logs in if
# StartWhenAvailable is set (which we do).
#
# Usage:
#     powershell -ExecutionPolicy Bypass -File scripts\install_scheduled_task.ps1
#
# To uninstall:
#     schtasks /delete /tn "nam-hedgefund-daily" /f
#
# To trigger a test run immediately:
#     schtasks /run /tn "nam-hedgefund-daily"

param(
    [string]$RunTime = "06:00",
    [string]$TaskName = "nam-hedgefund-daily"
)

$repoRoot = "C:\Users\user\Downloads\claude hedgefund"
$batPath  = Join-Path $repoRoot "scripts\run_daily.bat"

if (-not (Test-Path $batPath)) {
    Write-Error "Batch script not found at $batPath. Make sure the repo is at $repoRoot."
    exit 1
}

# Build the task definition
$action    = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $repoRoot
$trigger   = New-ScheduledTaskTrigger -Daily -At $RunTime
$settings  = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

# Remove existing task if it exists
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing scheduled task '$TaskName'..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Register
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "nam-hedgefund: daily bias engine run. Reads FRED + COT + prices, runs agent stack, writes bias_cards/{date}/." | Out-Null

Write-Host ""
Write-Host "Installed task '$TaskName'." -ForegroundColor Green
Write-Host "  Runs daily at $RunTime"
Write-Host "  Script:   $batPath"
Write-Host "  Logs:     $repoRoot\logs\bias_engine.log"
Write-Host ""
Write-Host "Test it now without waiting:"
Write-Host "  schtasks /run /tn `"$TaskName`""
Write-Host ""
Write-Host "Inspect or change schedule:"
Write-Host "  Open 'Task Scheduler' from Start Menu, find '$TaskName' under Task Scheduler Library."
Write-Host ""
Write-Host "Uninstall:"
Write-Host "  schtasks /delete /tn `"$TaskName`" /f"
