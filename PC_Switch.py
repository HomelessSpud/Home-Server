from flask import Flask, request, abort
import RPi.GPIO as GPIO
import time

POWER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_PIN, GPIO.OUT, initial=GPIO.LOW)

def press_power():
    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(POWER_PIN, GPIO.LOW)

app = Flask(__name__)

@app.route("/api/power", methods=["POST"])
def power():
    token = request.headers.get("X-Auth")
    if token != "YOUR_SECRET_TOKEN":
        abort(403)
    press_power()
    return "OK"

app.run(host="0.0.0.0", port=5000)
