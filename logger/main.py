import time
from picamera2 import Picamera2
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


picam = Picamera2()
config = picam.create_video_configuration(main={"size": (1280, 720)})  # Reduced frame rate
picam.configure(config)

picam.configure(config)
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


def generate_or_append_csv( data):
    """
    Generates a CSV file or appends data if the file already exists.
    
    Parameters:
    - filename: The path to the file where the CSV will be saved or appended.
    - data: A list of dictionaries, where each dictionary represents a row of data.
           Expected keys are 'time', 'temperature', 'humidity', and 'media'.
    """
    
    # Check if the file exists
    filename = "data.csv"
    file_exists = os.path.isfile(filename)
    
    # Open the file in append mode if it exists, otherwise write mode
    with open(filename, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        
        # Write the header if the file does not exist
        if not file_exists:
            writer.writerow(['time', 'temperature', 'humidity', 'media'])
        
        # Iterate over the data and write each row
        for row in data:
            writer.writerow([row['time'], row['temperature'], row['humidity'], row['media']])
            
    print(f"Data {'appended to' if file_exists else 'written to'} '{filename}' successfully.")



def upload_jpg_file(filename):
    url = "https://api.spaia.co.za/media"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    with open(filename, "rb") as file:
        files = {"file": (filename, file, "image/jpeg")}
        response = requests.post(url, files=files, headers=headers)

        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print("Failed to upload the file. Error:", response.text)
def upload_csv_file():
    url = "https://api.spaia.co.za/field/events"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    file_path = 'data.csv'
    try:
        with open(file_path, "rb") as file:
            files = {"events": (file_path, file)}
            response = requests.post(url, files=files, headers=headers)

            if response.status_code in [200, 201]:  # Assuming 201 could also be a success
                print("CSV File uploaded successfully.")
            else:
                print(f"Failed to upload the CSV file. Status code: {response.status_code}, Error:", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

def captureData():
     # MODE_SLEEP, MODE_FORCED, MODE_NORMAL is valid. See 3.3
    now = datetime.now()
    file_name = now.strftime("%Y-%m-%d_%H-%M-%S")
    img_name = f"images/{file_name}.jpg"
    if(mySensor.connected):
        mySensor.mode = mySensor.MODE_NORMAL
        data = [
        {"time": datetime.now().timestamp(), "temperature": mySensor.temperature_celsius, "humidity": mySensor.humidity, "media": f"{file_name}.jpg"}
        ]
        mySensor.mode = mySensor.MODE_SLEEP # MODE_SLEEP, MODE_FORCED, MODE_NORMAL is valid. See 3.3
    else:
        data = [
        {"time": datetime.now().timestamp(), "temperature": 0, "humidity":0, "media": f"{file_name}.jpg"}
        ]
   
    
    generate_or_append_csv(data)
    picam.start()
    # time.sleep(2)  # Let camera warm up

    picam.capture_file(img_name)  # Fixed missing variable usage
    upload_csv_file();
    upload_jpg_file(img_name)

    picam.stop()  # Use stop instead of close to keep the session for the next capture
    try:
        os.remove(img_name)
        print(f"Successfully deleted {img_name}")
        os.remove('data.csv')
        print("deleted data.csv")
    except OSError as e:
        print(f"Error: {e.strerror} - {e.filename}")


try:
    while True:
        captureData()
        time.sleep(10)  # Wait for 10 seconds before the next capture
except KeyboardInterrupt:
    print("Stopped by user")
# Blinky.fill(0,0,0)