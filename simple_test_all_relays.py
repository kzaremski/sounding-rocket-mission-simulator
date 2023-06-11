"""
    simple_Test_all_relays.py
        Test all relays
"""

# Import dependencies
import RPi.GPIO as GPIO
import configparser
import time 
import sys

# Command line arguments
arguments = sys.argv

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

# Timing Event Relay Channels
channels = [
    GSE_1_RELAY,
    GSE_2_RELAY,
    TE_R_A_RELAY,
    TE_R_B_RELAY,
    TE_1_RELAY,
    TE_2_RELAY,
    TE_3_RELAY,
]

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_SUPPLY_RELAY, GPIO.OUT)
GPIO.setup(GSE_1_RELAY, GPIO.OUT)
GPIO.setup(GSE_2_RELAY, GPIO.OUT)
GPIO.setup(TE_R_A_RELAY, GPIO.OUT)
GPIO.setup(TE_R_B_RELAY, GPIO.OUT)
GPIO.setup(TE_1_RELAY, GPIO.OUT)
GPIO.setup(TE_2_RELAY, GPIO.OUT)
GPIO.setup(TE_3_RELAY, GPIO.OUT)

# Start the power supply
if "hold" in arguments: input()
else: time.sleep(4)
GPIO.output(POWER_SUPPLY_RELAY, GPIO.HIGH)

# How long to wait when not holding
wait = 0.3

# Wait for enter if hold mode or wait 4 seconds
if "hold" in arguments: input()
else: time.sleep(4)

# Loop through and turn on and off the relays one by one
for channel in channels:
    GPIO.output(channel, GPIO.HIGH)
    if "hold" in arguments: input()
    else: time.sleep(wait)
    GPIO.output(channel, GPIO.LOW)

# Turn on all relays one by one
for channel in channels:
    GPIO.output(channel, GPIO.HIGH)
    if "hold" in arguments: input()
    else: time.sleep(wait)

# Turn off all relays one by one
for channel in channels:
    GPIO.output(channel, GPIO.LOW)
    if "hold" in arguments: input()
    else: time.sleep(wait)

# Wait for enter if hold mode or wait 4 seconds
if "hold" in arguments: input()
else: time.sleep(4)

# Shut off main power
GPIO.output(POWER_SUPPLY_RELAY, GPIO.LOW)
