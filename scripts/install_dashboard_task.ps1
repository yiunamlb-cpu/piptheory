# Registers the Streamlit dashboard auto-start task with Windows Task Scheduler.
#
# Trigger: at user logon. Means the dashboard is reachable on the tailnet
# whenever the laptop is on and you're logged in.
#
# Usage:
#     powershell -ExecutionPolicy Bypass -File scripts\install_dashboard_task.ps1
#
# To uninstall:
#     schtasks /delete /tn "nam-hedgefund-dashboard" /f
#
# To trigger now:
#     schtasks /run /tn "nam-hedgefund-dashboard"

param(
    [string]$TaskName = "nam-hedgefund-dashboard"
)

$repoRoot = "C:\Users\user\Downloads\claude hedgefund"
$batPath  = Join-Path $repoRoot "scripts\run_dashboard.bat"

if (-not (Test-Path $batPath)) {
    Write-Error "Batch script not found at $batPath."
    exit 1
}

$action    = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $repoRoot
$trigger   = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$settings  = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task '$TaskName'..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "nam-hedgefund: auto-start the Streamlit dashboard at login. Tailscale Serve mapping re-applied on every start so the https://desktop.tail*.ts.net/ URL works post-reboot." | Out-Null

Write-Host ""
Write-Host "Installed task '$TaskName'." -ForegroundColor Green
Write-Host "  Trigger: at user logon"
Write-Host "  Script:  $batPath"
Write-Host "  Logs:    $repoRoot\logs\dashboard.log"
Write-Host ""
Write-Host "Test it now without rebooting:"
Write-Host "  schtasks /run /tn `"$TaskName`""
Write-Host ""
Write-Host "Uninstall:"
Write-Host "  schtasks /delete /tn `"$TaskName`" /f"
