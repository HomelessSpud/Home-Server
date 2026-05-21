param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath,

    [string]$TaskName = "MinecraftStart",

    [string]$Description = "Start Minecraft server from start.bat on demand"
)

$ErrorActionPreference = "Stop"

$BatchPath = $BatchPath.TrimEnd('\', '/')

if (-not (Test-Path -LiteralPath $BatchPath)) {
    throw "Batch file not found: $BatchPath"
}

$batchFullPath = (Resolve-Path -LiteralPath $BatchPath).Path
$workingDir = Split-Path -Path $batchFullPath -Parent
$wrapperPath = Join-Path $workingDir "MinecraftStartWrapper.cmd"

@"
@echo off
cd /d "$workingDir"
call "$batchFullPath"
"@ | Set-Content -LiteralPath $wrapperPath -Encoding ASCII

# Run the generated wrapper so Task Scheduler does not need to parse the .bat path itself.
$action = New-ScheduledTaskAction -Execute $wrapperPath -WorkingDirectory $workingDir

# Dummy far-future trigger keeps the task available for on-demand starts only.
$trigger = New-ScheduledTaskTrigger -Once -At "2099-01-01T00:00:00"

# SYSTEM account avoids interactive login requirements.
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

$task = New-ScheduledTask -Action $action -Principal $principal -Trigger $trigger -Settings $settings -Description $Description

Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

Write-Host "Task '$TaskName' created/updated."
Write-Host "Batch path: $batchFullPath"
Write-Host "Wrapper path: $wrapperPath"
Write-Host "Working directory: $workingDir"
Write-Host "Test run command: schtasks /Run /TN \"$TaskName\""
