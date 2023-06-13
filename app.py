"""
    RockSat-X Sounding Rocket Mission Simulator
        This is a web app that drives a simulator appliance comprised of an eight-channel relay controller
        (with a master relay and 7 channels representing the NASA Wallops timing events), an RS232 serial input
        port that represents spacecraft telemetry, and and ammeter to monitor current draw of the payload.
"""

# See if we are running on linux
import sys
linuxSystem = sys.platform == "linux" or sys.platform == "linux2"

# Import dependencies
from flask import Flask, render_template, send_from_directory, request
import configparser
import time 
from database import Database
import asyncio
import json
from flask_socketio import SocketIO, send
# If we are running in test mode on a non Pi computer, do not import GPIO module
if linuxSystem: import RPi.GPIO as GPIO
 
# Flask Application Instance
app = Flask(__name__)
# Add websocket support
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Load constants from config file
config = configparser.ConfigParser()
config.read("./config.ini")
POWER_SUPPLY_RELAY = int(config["Pinout"]["POWER_SUPPLY_RELAY"])
GSE_1_RELAY = int(config["Pinout"]["GSE_1_RELAY"])
GSE_2_RELAY = int(config["Pinout"]["GSE_2_RELAY"])
TE_R_A_RELAY = int(config["Pinout"]["TE_R_A_RELAY"])
TE_R_B_RELAY = int(config["Pinout"]["TE_R_B_RELAY"])
TE_1_RELAY = int(config["Pinout"]["TE_1_RELAY"])
TE_2_RELAY = int(config["Pinout"]["TE_2_RELAY"])
TE_3_RELAY = int(config["Pinout"]["TE_3_RELAY"])
PORT = int(config["App"]["PORT"])

# Init the database
database = Database("database.sqlite")

# Setup GPIO pins (if we are running on a Raspberry Pi)
if linuxSystem:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_SUPPLY_RELAY, GPIO.OUT)
    GPIO.setup(GSE_1_RELAY, GPIO.OUT)
    GPIO.setup(GSE_2_RELAY, GPIO.OUT)
    GPIO.setup(TE_R_A_RELAY, GPIO.OUT)
    GPIO.setup(TE_R_B_RELAY, GPIO.OUT)
    GPIO.setup(TE_1_RELAY, GPIO.OUT)
    GPIO.setup(TE_2_RELAY, GPIO.OUT)
    GPIO.setup(TE_3_RELAY, GPIO.OUT)

# Monitor telemetry (if we are running on a RaspberryPi)
telemetryOutput = ""
def monitorTelemetry():
    pass
if linuxSystem:
    pass

# State websocket
@socketio.on("message")
def handle_message(message):
    send(json.dumps(
            {
            "channels": {
                "POWER_SUPPLY_RELAY": GPIO.input(POWER_SUPPLY_RELAY),
                "GSE_1_RELAY": GPIO.input(GSE_1_RELAY),
                "GSE_2_RELAY": GPIO.input(GSE_2_RELAY),
                "TE_R_A_RELAY": GPIO.input(TE_R_A_RELAY),
                "TE_R_B_RELAY": GPIO.input(TE_R_B_RELAY),
                "TE_1_RELAY": GPIO.input(TE_1_RELAY),
                "TE_2_RELAY": GPIO.input(TE_2_RELAY),
                "TE_3_RELAY": GPIO.input(TE_3_RELAY),
            },
            "time": {
                "launch": 0.0,
                "event": 0.0,
                "dwell": 0.0,
            }
        }))

# Root
@app.route("/")
@app.route("/run")
@app.route("/manual")
@app.route("/telemetry")
def hello_world():
    return render_template("index.html")

# Manual Control
@app.route("/api/manual/<channel>")
def handleManualControl(channel):
    print(channel)
    if channel == "KILL":
        GPIO.output(POWER_SUPPLY_RELAY, GPIO.LOW)
        GPIO.output(GSE_1_RELAY, GPIO.LOW)
        GPIO.output(GSE_2_RELAY, GPIO.LOW)
        GPIO.output(TE_R_A_RELAY, GPIO.LOW)
        GPIO.output(TE_R_B_RELAY, GPIO.LOW)
        GPIO.output(TE_1_RELAY, GPIO.LOW)
        GPIO.output(TE_2_RELAY, GPIO.LOW)
        GPIO.output(TE_3_RELAY, GPIO.LOW)
        return "Done!"
    
    channels = {
        "POWER_SUPPLY_RELAY": POWER_SUPPLY_RELAY,
        "GSE_1_RELAY": GSE_1_RELAY,
        "GSE_2_RELAY": GSE_2_RELAY,
        "TE_R_A_RELAY": TE_R_A_RELAY,
        "TE_R_B_RELAY": TE_R_B_RELAY,
        "TE_1_RELAY": TE_1_RELAY,
        "TE_2_RELAY": TE_2_RELAY,
        "TE_3_RELAY": TE_3_RELAY,
    }
    channel = channels[channel]
    
    if GPIO.input(channel): GPIO.output(channel, GPIO.LOW)
    else: GPIO.output(channel, GPIO.HIGH)
    
    return "Done!"

# Static files
@app.route("/static/<path:path>")
def send_static_resource(path):
    return send_from_directory("static", path)

# Run if not a module
if __name__ == "__main__":
    socketio.run(app, port=PORT)
    database.close()
