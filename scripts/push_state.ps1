# push_state.ps1  —  Run after the daily pipeline completes.
# Commits all public-safe data files and pushes to GitHub,
# which triggers Render auto-redeploy with fresh data.
#
# Usage:   .\scripts\push_state.ps1
# Add to scheduled task:  chain after pipeline with  && powershell -File scripts\push_state.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

# Push state + bias_cards so they persist across Render deploys
$stateFiles = @(
    "state/score_history.json",
    "state/thesis_tracker.json"
)

$changed = $false
foreach ($f in $stateFiles) {
    if (Test-Path $f) {
        git add --force $f
        $changed = $true
    }
}

# Bias cards contain the actual run data — commit so deploys don't wipe analysis
$biasDir = "bias_cards"
if (Test-Path $biasDir) {
    Get-ChildItem -Path $biasDir -Directory | ForEach-Object {
        git add "$biasDir/$($_.Name)/"
        $changed = $true
    }
}

if (-not $changed) {
    Write-Host "No state files to push."
    exit 0
}

# Check if there are staged changes
$diff = git diff --cached --name-only
if (-not $diff) {
    Write-Host "State files unchanged — nothing to push."
    exit 0
}

$date = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "state: daily pipeline update $date"
git push origin main

Write-Host "State pushed — Render will auto-redeploy."
