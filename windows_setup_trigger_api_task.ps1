param(
    [string]$TaskName = "MinecraftTriggerApi",
    [string]$PythonExe = "python",
    [string]$ScriptPath = ".\windows_minecraft_trigger.py",
    [string]$TriggerToken = "CHANGE_ME",
    [string]$Port = "8787"
)

$ErrorActionPreference = "Stop"

$scriptFullPath = (Resolve-Path -LiteralPath $ScriptPath).Path
$workingDir = Split-Path -Path $scriptFullPath -Parent
$venvDir = Join-Path $workingDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    & $PythonExe -m venv $venvDir
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install fastapi uvicorn

$arguments = ('"{0}" --token "{1}" --port "{2}"' -f $scriptFullPath, $TriggerToken, $Port)
$action = New-ScheduledTaskAction -Execute $venvPython -Argument $arguments -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

$task = New-ScheduledTask -Action $action -Principal $principal -Trigger $trigger -Settings $settings -Description "Starts local Minecraft trigger API at system boot"

Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

try {
    if (-not (Get-NetFirewallRule -DisplayName "Minecraft Trigger API" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -DisplayName "Minecraft Trigger API" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -Profile Private | Out-Null
    }
} catch {
    Write-Warning "Firewall rule could not be created automatically. Run PowerShell as Administrator and create it manually for port $Port."
}

Write-Host "Startup task '$TaskName' created/updated."
Write-Host "Python executable: $venvPython"
Write-Host "Trigger token: $TriggerToken"
Write-Host "API port: $Port"
