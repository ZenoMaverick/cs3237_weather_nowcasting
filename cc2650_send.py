# Make sure to install the necessary packages beforehand
# $ sudo apt-get install blues-utils libopenobex1 build-essential libglib2.0-dev libdbus-1-dev
# $ sudo service bluetooth restart

import time
import json
import struct
import sensortag
import paho.mqtt.client as mqtt
import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Use the command below in terminal to scan for mac address of sensortag
# $ hcitool -i hci1 lescan
# LE Scan ...
# B0:B4:48:BD:B8:05 CC2650 SensorTag

my_sensor = '54:6C:0E:52:EF:53' #mine
tag = sensortag.SensorTag(my_sensor)

print ("Connected to SensorTag", my_sensor)

sensorOn  = struct.pack("B", 0x01) #writing 0x01 enables data collection, 0x00 to disable
sensorbarcal =  struct.pack("B", 0x02)
# sensorMagOn = struct.pack("H", 0x0007)
# sensorGyrOn = struct.pack("H", 0x0007)
# sensorAccOn = struct.pack("H", 0x0038)

# Sensors used, the sensors below can be commented out for usage
# tag.IRtemperature.disable() # Sensortag model does not have IR Temp sensor
# tag.humidity.enable()
# tag.barometer.enable()
# tag.accelerometer.disable()
# tag.magnetometer.disable()
# tag.gyroscope.disable()
# tag.lightmeter.enable()
# tag.battery.enable()

tag.IRtemperature.disable() # Sensortag model does not have IR Temp sensor
tag.humidity.enable()
tag.barometer.enable()
tag.battery.enable()



def send_data(client):
    msg = []
    time.sleep(1.0)
    
    # Delete this later
    # ambient_temp, target_temp = tag.IRtemperature.read() # not included in sensortag
    #x_accel, y_accel, z_accel = tag.accelerometer.read()
    #lux = tag.lightmeter.read()

    #Used, do not delete
    ambient_temp_hum, rel_humidity = tag.humidity.read()
    ambient_temp_baro, pressure_millibars = tag.barometer.read()
    time_now = datetime.datetime.now().strftime("%d/%m/%y %X")
    
    # create data structure to be inserted into collection
    data = {
        'Localtime'    : datetime.datetime.now().strftime("%d/%m/%y %X"),
        'Ambient Temp'  : ambient_temp_hum,
        'Humidity'      : rel_humidity,
        'Pressure'     : pressure_millibars
    }
    payload = json.dumps(data)
    client.publish("iot/data", json.dumps(data))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to client")
        client.subscribe("iot/#")
    else:
        print("Failed to connnect. Error code %d." %rc)


def on_message(client, userdata, msg):
    #print("Received message from server")
    resp_dict = json.loads(msg.payload)
    print("Localtime: %s, Ambient Temp: %f, Humidity: %f, Pressure: %f"
        %(resp_dict["Localtime"], resp_dict["Ambient Temp"], resp_dict["Humidity"], resp_dict["Pressure"]))


def setup(hostname):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)
    client.loop_start()
    return client


def main():
    client = setup("localhost")
    print("Sending data")
    while True:
        time1 = time.time() #get time now
        send_data(client)
        time2 = time.time() - time1 #subtract time1 to get time taken for send_data process
        time.sleep(3600-time2) #1hr samples
        #time.sleep(30-time2) #subtract the time taken for the process in front
        
if __name__ == '__main__':
    main()
