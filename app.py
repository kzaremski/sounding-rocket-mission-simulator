# import flask module
from flask import Flask
import configparser
 
# instance of flask application
app = Flask(__name__)

# Load GPIO

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

# Root
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Run if not a module
if __name__ == "__main__":
    app.run(debug=True, port=PORT)
