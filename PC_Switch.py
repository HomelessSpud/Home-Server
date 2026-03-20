from flask import Flask, request, abort, send_from_directory
import RPi.GPIO as GPIO
import time
import os

POWER_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_PIN, GPIO.OUT, initial=GPIO.LOW)

def press_power():
    print("POWER PRESSED")
    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(POWER_PIN, GPIO.LOW)

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("/home/ethan/Documents/Server/Home-Server-PC-Switch/", "index.html")

@app.route("/api/power", methods=["POST"])
def power():
    token = request.headers.get("X-Auth")
    if token != "Event":
        abort(403)
    press_power()
    return "OK"

app.run(host="0.0.0.0", port=5000)
