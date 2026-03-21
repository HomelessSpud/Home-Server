import lgpio
import time
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse


app = FastAPI()

POWER_PIN = 17

# Open the GPIO chip
h = lgpio.gpiochip_open(0)

# Set pin as output
lgpio.gpio_claim_output(h, POWER_PIN)

def press_power():
    lgpio.gpio_write(h, POWER_PIN, 1)
    time.sleep(0.3)
    lgpio.gpio_write(h, POWER_PIN, 0)

@app.post("/api/power")
def power(x_auth: str = Header(None)):
    if x_auth != "YOUR_SECRET_TOKEN":
        raise HTTPException(status_code=403)
    press_power()
    return {"status": "ok"}

@app.get("/")
def index():
    return FileResponse("index.html")
