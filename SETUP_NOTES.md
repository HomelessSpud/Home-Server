# Setup Notes

## Windows PC

Create the on-demand Minecraft task:

```powershell
Set-Location "C:\Users\ethan\Documents\Things\Home Server\Home-Server-PC-Switch"
.\windows_setup_task.ps1 -BatchPath "C:\Users\ethan\Documents\Minecraft Server\shared inv\start.bat" -TaskName "MinecraftStart"
```

Create the startup trigger API task:

```powershell
Set-Location "C:\Users\ethan\Documents\Things\Home Server\Home-Server-PC-Switch"
.\windows_setup_trigger_api_task.ps1 -TaskName "MinecraftTriggerApi" -PythonExe "python" -ScriptPath ".\windows_minecraft_trigger.py" -TriggerToken "7f3c9b2e-1a0d-4c8e-9f6b-2d6d8f4a91c7" -Port "8787"
```

Start and test the API:

```powershell
schtasks /Run /TN "MinecraftTriggerApi"
Invoke-WebRequest http://localhost:8787/health
```

## Pi / FastAPI app

Set these environment variables before starting the Pi app:

- `PC_HOST` = Windows PC IP or hostname
- `PC_READY_PORT` = port that becomes reachable when the PC is up, usually `3389`
- `PC_BOOT_TIMEOUT_SECONDS` = `300`
- `PC_BOOT_POLL_SECONDS` = `5`
- `MINECRAFT_START_URL` = `http://WINDOWS_PC_IP:8787/start-minecraft`
- `MINECRAFT_START_TOKEN` = `7f3c9b2e-1a0d-4c8e-9f6b-2d6d8f4a91c7`
- `PC_SWITCH_AUTH_TOKEN` = token used by the browser app for `/api/power` calls

## End-to-end test

1. Open the Pi web page.
2. Click Toggle Power.
3. Choose yes when prompted to start Minecraft.
4. Confirm the Windows PC boots.
5. Confirm the Minecraft task starts automatically after the PC becomes reachable.
