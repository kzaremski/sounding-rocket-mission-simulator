"""
    RockSat-X Sounding Rocket Mission Simulator
        This is a web app that drives a simulator appliance comprised of an eight-channel relay controller
        (with a master relay and 7 channels representing the NASA Wallops timing events), an RS232 serial input
        port that represents spacecraft telemetry, and and ammeter to monitor current draw of the payload.
"""

# Import dependencies
from flask import Flask, render_template, send_from_directory, request, jsonify
import configparser
import time 
import os
from database import Database
import multiprocessing
import traceback
import json
from flask_socketio import SocketIO, send
import RPi.GPIO as GPIO
import serial
 
# Flask Application Instance
app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_SUPPLY_RELAY, GPIO.OUT)
GPIO.setup(GSE_1_RELAY, GPIO.OUT)
GPIO.setup(GSE_2_RELAY, GPIO.OUT)
GPIO.setup(TE_R_A_RELAY, GPIO.OUT)
GPIO.setup(TE_R_B_RELAY, GPIO.OUT)
GPIO.setup(TE_1_RELAY, GPIO.OUT)
GPIO.setup(TE_2_RELAY, GPIO.OUT)
GPIO.setup(TE_3_RELAY, GPIO.OUT)

# Turn off all outputs
GPIO.output(POWER_SUPPLY_RELAY, GPIO.LOW)
GPIO.output(GSE_1_RELAY, GPIO.LOW)
GPIO.output(GSE_2_RELAY, GPIO.LOW)
GPIO.output(TE_R_A_RELAY, GPIO.LOW)
GPIO.output(TE_R_B_RELAY, GPIO.LOW)
GPIO.output(TE_1_RELAY, GPIO.LOW)
GPIO.output(TE_2_RELAY, GPIO.LOW)
GPIO.output(TE_3_RELAY, GPIO.LOW)    

# Monitor telemetry (if we are running on a RaspberryPi)
telemetrySerial = serial.Serial(
    port="/dev/ttyS0",
    baudrate=19200,
    timeout=None
)
def monitorTelemetry():
    # Loop and add serial output to the telemetry output string forever
    while True:
        next = str(telemetrySerial.read(1).decode('utf-8'))
        with open("./telemetry.txt", "a") as file:
            file.write(next)
            file.flush()

# Configure multiprocessing
multiprocessing.set_start_method("fork")
processQueue = multiprocessing.Queue()

# Mission state variables
missionThread = None
missionState = "ready"
missionTime = multiprocessing.Value('d', 0.0)
missionNextTimer = multiprocessing.Value('d', 0.0)
missionCurrentDwell = multiprocessing.Value('d', 0.0)
def simulator(missionParameters, missionTime, missionNextTimer, missionCurrentDwell):
    try:
        events = [
            "GSE-1",
            "GSE-2",
            "TE-Ra",
            "TE-Rb",
            "TE-1",
            "TE-2",
            "TE-3",
        ]
        eventChannels = {
            "GSE-1": GSE_1_RELAY,
            "GSE-2": GSE_2_RELAY,
            "TE-Ra": TE_R_A_RELAY,
            "TE-Rb": TE_R_B_RELAY,
            "TE-1": TE_1_RELAY,
            "TE-2": TE_1_RELAY,
            "TE-3": TE_1_RELAY
        }
        fired = []

        # Sorted list of 
        def sortSecond(val):
            return val[1]
        activeEvents = [i for i in list(missionParameters.values()) if i[3] == 1]
        activeEvents.sort(key=sortSecond)

        # Find the lowest enabled event
        lowestEnabledEvent = None
        for timerEvent in events:
            if lowestEnabledEvent == None and missionParameters[timerEvent][3]:
                lowestEnabledEvent = timerEvent
            elif missionParameters[timerEvent][3] and missionParameters[timerEvent][1] < missionParameters[lowestEnabledEvent][1]:
                lowestEnabledEvent = timerEvent

        # Set mission state
        missionState = "running"

        running = True
        GPIO.output(POWER_SUPPLY_RELAY, GPIO.HIGH) # Start the master power
        startTime = time.time()
        while running:
            # Calculate mission time
            missionTime.value = time.time() - abs(missionParameters[lowestEnabledEvent][1]) - 10 - startTime
            
            for timerEvent in events:
                # Fire the timer event
                if timerEvent not in fired and missionParameters[timerEvent][3] == 1 and missionTime.value >= missionParameters[timerEvent][1]:
                    fired.append(timerEvent)
                    GPIO.output(eventChannels[timerEvent], GPIO.HIGH)
                # Fire the dwell (off signal)
                if "D" + timerEvent not in fired and missionParameters[timerEvent][3] == 1 and missionTime.value >= missionParameters[timerEvent][1] + missionParameters[timerEvent][2]:
                    fired.append("D" + timerEvent)
                    GPIO.output(eventChannels[timerEvent], GPIO.LOW)
                # Compute current dwell time
                if "GSE" not in timerEvent and timerEvent in fired and "D" + timerEvent not in fired:
                    missionCurrentDwell.value = missionParameters[timerEvent][1] + missionParameters[timerEvent][2] - missionTime.value

            # Try and calculate the next timer event
            for parameter in activeEvents:
                if parameter[0] not in fired:
                    missionNextTimer.value = parameter[1] - missionTime.value
                    break

    except Exception as e:
        print(traceback.format_exc())
    
    # Turn off all outputs
    GPIO.output(POWER_SUPPLY_RELAY, GPIO.LOW)
    GPIO.output(GSE_1_RELAY, GPIO.LOW)
    GPIO.output(GSE_2_RELAY, GPIO.LOW)
    GPIO.output(TE_R_A_RELAY, GPIO.LOW)
    GPIO.output(TE_R_B_RELAY, GPIO.LOW)
    GPIO.output(TE_1_RELAY, GPIO.LOW)
    GPIO.output(TE_2_RELAY, GPIO.LOW)
    GPIO.output(TE_3_RELAY, GPIO.LOW)    

# Automated Mission Operation
@app.route("/api/mission/start")
def startMission():
    global missionState
    global missionThread
    if missionState != "ready": return "No! " + missionState
    
    missionParameters = {
        "GSE-1": database.getTimerEvent("GSE-1"),
        "GSE-2": database.getTimerEvent("GSE-2"),
        "TE-Ra": database.getTimerEvent("TE-Ra"),
        "TE-Rb": database.getTimerEvent("TE-Rb"),
        "TE-1": database.getTimerEvent("TE-1"),
        "TE-2": database.getTimerEvent("TE-2"),
        "TE-3": database.getTimerEvent("TE-3"),
    }
    
    missionThread = multiprocessing.Process(target=simulator, args=[
        missionParameters,
        missionTime,
        missionNextTimer,
        missionCurrentDwell,
    ])
    missionThread.start()
    missionState = "running"

    return "Done!"
@app.route("/api/mission/pause")
def pauseMission():
    global missionState
    global missionThread

    if missionState == "ready": return "No!"

    # Kill the mission process
    if missionThread != None:
        missionThread.terminate()
        missionThread.join()

    # Reset times
    missionTime.value = 0.0
    missionNextTimer.value = 0.0
    missionCurrentDwell.value = 0.0
    
    return "Done!"
@app.route("/api/mission/reset")
def resetMission():
    global missionState
    global missionThread

    if missionState == "ready": return "No!"
    
    # Kill the mission process
    if missionThread != None:
        missionThread.terminate()
        missionThread.join()

    # Reset times
    missionTime.value = 0.0
    missionNextTimer.value = 0.0
    missionCurrentDwell.value = 0.0

    # Turn off all outputs
    GPIO.output(POWER_SUPPLY_RELAY, GPIO.LOW)
    GPIO.output(GSE_1_RELAY, GPIO.LOW)
    GPIO.output(GSE_2_RELAY, GPIO.LOW)
    GPIO.output(TE_R_A_RELAY, GPIO.LOW)
    GPIO.output(TE_R_B_RELAY, GPIO.LOW)
    GPIO.output(TE_1_RELAY, GPIO.LOW)
    GPIO.output(TE_2_RELAY, GPIO.LOW)
    GPIO.output(TE_3_RELAY, GPIO.LOW)

    # Reset mission state
    missionState = "ready"

    return "Done!"

# State websocket
@socketio.on("message")
def handle_message(message):
    global missionState
    global missionTime
    global missionNextTimer
    global missionCurrentDwell
    
    output = json.dumps(
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
                "launch": missionTime.value,
                "event": missionNextTimer.value,
                "dwell": missionCurrentDwell.value,
            },
            "mission": missionState
        }
    )


    send(output)

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

# Mission Parameters Management
@app.route("/api/mission/get")
def getMissionParameters():
    return json.dumps({
        "GSE-1": database.getTimerEvent("GSE-1"),
        "GSE-2": database.getTimerEvent("GSE-2"),
        "TE-Ra": database.getTimerEvent("TE-Ra"),
        "TE-Rb": database.getTimerEvent("TE-Rb"),
        "TE-1": database.getTimerEvent("TE-1"),
        "TE-2": database.getTimerEvent("TE-2"),
        "TE-3": database.getTimerEvent("TE-3"),
    })
@app.route("/api/mission/set", methods=['POST'])
def setMissionParameters():
    json = request.json
    if "GSE-1" in json: database.updateTimerEvent("GSE-1", json["GSE-1"]["time"], json["GSE-1"]["dwell"], json["GSE-1"]["enabled"])
    if "GSE-2" in json: database.updateTimerEvent("GSE-2", json["GSE-2"]["time"], json["GSE-2"]["dwell"], json["GSE-2"]["enabled"])
    if "TE-Ra" in json: database.updateTimerEvent("TE-Ra", json["TE-Ra"]["time"], json["TE-Ra"]["dwell"], json["TE-Ra"]["enabled"])
    if "TE-Rb" in json: database.updateTimerEvent("TE-Rb", json["TE-Rb"]["time"], json["TE-Rb"]["dwell"], json["TE-Rb"]["enabled"])
    if "TE-1" in json: database.updateTimerEvent("TE-1", json["TE-1"]["time"], json["TE-1"]["dwell"], json["TE-1"]["enabled"])
    if "TE-2" in json: database.updateTimerEvent("TE-2", json["TE-2"]["time"], json["TE-2"]["dwell"], json["TE-2"]["enabled"])
    if "TE-3" in json: database.updateTimerEvent("TE-3", json["TE-3"]["time"], json["TE-3"]["dwell"], json["TE-3"]["enabled"])
    return "Done!"

# Telemetry
telemetryMonitorThread = multiprocessing.Process(target=monitorTelemetry, args=[])
telemetryMonitorThread.start()

@app.route("/api/telemetry/get")
def getTelemetry():
    telemetryOutput = ""
    with open("./telemetry.txt", "r") as file:
        telemetryOutput = file.read()
    return telemetryOutput
@app.route("/api/telemetry/clear")
def clearTelemetry():
    os.system("echo \" \" > ./telemetry.txt")
    return "Done!"

# Static files
@app.route("/static/<path:path>")
def send_static_resource(path):
    return send_from_directory("static", path)

# Run if not a module
if __name__ == "__main__":
    socketio.run(app, port=PORT, allow_unsafe_werkzeug=True)
    database.close()
