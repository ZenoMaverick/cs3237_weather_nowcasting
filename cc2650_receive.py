import paho.mqtt.client as mqtt
import numpy as np
import json
import time
import csv
from itertools import cycle
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Connect to Mongo server
# found in mongodb->connect->connect your application -> copy the connection string and replace <password> with your own password
mongoClient = MongoClient('mongodb+srv://Zeno:vx8WC8mBz69kaHaU@sensortag.b4min.mongodb.net/<dbname>?retryWrites=true&w=majority', serverSelectionTimeoutMS = 3660)
db = mongoClient.sensortag # create database in our cluster
collection = db.data # create a collection


def on_connect(client, userdata,flags, rc):
	if rc == 0:
		print("Successfully connected to the broker.")
		client.subscribe("iot/#")
	else:
		print("Connection failed with code: %d." %rc)


def on_message(client, userdata, msg):
	# Convert message payload into a python dictionary
	recv_dict = json.loads(msg.payload)
	
	# Format the data back to json to be saved into mongodb
	data = {
        'Localtime'	: recv_dict["Localtime"],
        'Ambient Temp'  : recv_dict["Ambient Temp"],
        'Humidity'      : recv_dict["Humidity"],
        'Pressure'     : recv_dict["Pressure"]
    }
	csvdata = (data["Localtime"], data["Ambient Temp"], data["Humidity"], data["Pressure"])

    # Print whatever was received from client in terminal to compare with cc2650_send.py
	print("Localtime: %s, Ambient Temp: %f, Humidity: %f, Pressure: %f, ACK"
		%(data["Localtime"], data["Ambient Temp"], data["Humidity"], data["Pressure"]))
	
	
	# Test saving to mongo database
	try:
	 	# write_to_csv(csvdata) # saves to local csv file
		collection.insert_one(data)
	except BulkWriteError as bwe:
	 	print(bwe.details)
	

def setup(hostname):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(hostname)
	client.loop_forever()
	return client


def main():
	setup("localhost")
	while True:
		pass

# Can save to local csv file
def write_to_csv(data):
	# Save the data to a csv file
	with open('data.csv', 'a') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(data)


if __name__ == '__main__':
	main()
