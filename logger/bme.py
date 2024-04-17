import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import csv
import qwiic_bme280
import sys


# Load environment variables from .env file
load_dotenv()

# Access your API token
api_token = os.getenv('API_TOKEN')



mySensor = qwiic_bme280.QwiicBme280()
if mySensor.connected == False:
    print("The Qwiic BME280 device isn't connected to the system. Please check your connection",  file=sys.stderr)
else:
    print("BME found")
    mySensor.begin()

    mySensor.filter = 1  		# 0 to 4 is valid. Filter coefficient. See 3.4.4
    mySensor.standby_time = 0	# 0 to 7 valid. Time between readings. See table 27.

    mySensor.over_sample = 1			# 0 to 16 are valid. 0 disables temp sensing. See table 24.
    mySensor.pressure_oversample = 1	# 0 to 16 are valid. 0 disables pressure sensing. See table 23.
    mySensor.humidity_oversample = 1	# 0 to 16 are valid. 0 disables humidity sensing. See table 19.
    mySensor.mode = mySensor.MODE_NORMAL # MODE_SLEEP, MODE_FORCED, MODE_NORMAL is valid. See 3.3

    print(mySensor.temperature_celsius)


