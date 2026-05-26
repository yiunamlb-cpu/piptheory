# Register the central-bank-statement auto-fetch as a Windows scheduled task.
# Runs daily at 7am — covers the morning after FOMC/ECB/BoE/BoJ meetings
# without needing per-meeting scheduling. Idempotent (re-running replaces
# the existing task).
#
# Install:
#   .\scripts\install_fetch_statements_task.ps1
#
# Remove:
#   Unregister-ScheduledTask -TaskName "Piptheory-FetchStatements" -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName = "Piptheory-FetchStatements"
$repo = "C:\Users\user\Downloads\claude hedgefund"
$wrapper = Join-Path $repo "scripts\fetch_statements_wrapper.vbs"

if (-not (Test-Path $wrapper)) {
    Write-Error "Wrapper not found: $wrapper"
    exit 1
}

# Idempotent install
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Launch via wscript.exe — windowless, no console flash on tick.
$action = New-ScheduledTaskAction `
    -Execute "wscript.exe" `
    -Argument "`"$wrapper`""

# Daily 7am — captures the morning after evening (US) and afternoon (EU)
# central-bank meetings. The script is idempotent and silent when nothing
# new is published.
$trigger = New-ScheduledTaskTrigger -Daily -At 7am

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Daily 7am: fetch latest FOMC/ECB/BoE/BoJ statements into data/{fomc,ecb,boe,boj}_latest.txt. Idempotent and silent."

Write-Host "Installed scheduled task: $taskName" -ForegroundColor Green
Write-Host "  Runs daily at 7am."
Write-Host "  Output appended to logs\fetch_statements.log"
Write-Host ""
Write-Host "To verify: Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
Write-Host "To remove: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
