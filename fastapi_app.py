import json
import logging
import os
import socket
import threading
import time
import urllib.error
import urllib.request

import lgpio
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
logger = logging.getLogger(__name__)

app.mount("/static", StaticFiles(directory="."), name="static")

POWER_PIN = 17
AUTH_TOKEN = os.getenv("PC_SWITCH_AUTH_TOKEN", "YOUR_SECRET_TOKEN")
PC_HOST = os.getenv("PC_HOST", "")
PC_READY_PORT = int(os.getenv("PC_READY_PORT", "3389"))
PC_BOOT_TIMEOUT_SECONDS = int(os.getenv("PC_BOOT_TIMEOUT_SECONDS", "300"))
PC_BOOT_POLL_SECONDS = int(os.getenv("PC_BOOT_POLL_SECONDS", "5"))
MINECRAFT_START_URL = os.getenv("MINECRAFT_START_URL", "")
MINECRAFT_START_TOKEN = os.getenv("MINECRAFT_START_TOKEN", "")

gpio_handle = None
gpio_available = False


@app.on_event("startup")
def startup_gpio() -> None:
    global gpio_handle, gpio_available

    try:
        gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(gpio_handle, POWER_PIN)
        gpio_available = True
        logger.info("GPIO %s claimed successfully.", POWER_PIN)
    except lgpio.error as exc:
        gpio_handle = None
        gpio_available = False
        logger.error("GPIO %s is busy or unavailable: %s", POWER_PIN, exc)


@app.on_event("shutdown")
def shutdown_gpio() -> None:
    global gpio_handle, gpio_available

    if gpio_handle is not None:
        try:
            lgpio.gpiochip_close(gpio_handle)
        finally:
            gpio_handle = None
            gpio_available = False

@app.get("/")
def index():
    return FileResponse("index.html")

def press_power():
    if not gpio_available or gpio_handle is None:
        raise HTTPException(status_code=503, detail="GPIO pin is busy or unavailable")

    lgpio.gpio_write(gpio_handle, POWER_PIN, 1)
    time.sleep(0.3)
    lgpio.gpio_write(gpio_handle, POWER_PIN, 0)


def _is_pc_online() -> bool:
    if not PC_HOST:
        return False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        try:
            sock.connect((PC_HOST, PC_READY_PORT))
            return True
        except OSError:
            return False


def _wait_for_pc_boot() -> bool:
    deadline = time.time() + PC_BOOT_TIMEOUT_SECONDS
    while time.time() < deadline:
        if _is_pc_online():
            return True
        time.sleep(PC_BOOT_POLL_SECONDS)
    return False


def _start_minecraft_server() -> None:
    if not MINECRAFT_START_URL:
        raise RuntimeError("MINECRAFT_START_URL is not configured")

    payload = json.dumps({"action": "start_minecraft"}).encode("utf-8")
    request = urllib.request.Request(
        MINECRAFT_START_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Auth": MINECRAFT_START_TOKEN,
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10):
        return


def _boot_and_start_minecraft() -> None:
    if _wait_for_pc_boot():
        try:
            _start_minecraft_server()
        except (RuntimeError, urllib.error.URLError, TimeoutError, OSError):
            # Background thread should never crash the API request handler.
            return

@app.post("/api/power")
def power(x_auth: str = Header(None)):
    if x_auth != AUTH_TOKEN:
        raise HTTPException(status_code=403)
    press_power()
    return {"status": "ok"}


@app.post("/api/power-and-minecraft")
def power_and_minecraft(x_auth: str = Header(None)):
    if x_auth != AUTH_TOKEN:
        raise HTTPException(status_code=403)

    if not MINECRAFT_START_URL:
        raise HTTPException(status_code=400, detail="MINECRAFT_START_URL is not configured")

    press_power()

    thread = threading.Thread(target=_boot_and_start_minecraft, daemon=True)
    thread.start()

    return {
        "status": "ok",
        "message": "Power command sent. Minecraft start scheduled after boot.",
    }
