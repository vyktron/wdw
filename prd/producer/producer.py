import os
from kafka import KafkaProducer
import json
import random
import time
import socket
import math
from geopy.distance import distance

# Get the bootstrap server from the environment variable
bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         key_serializer=str.encode,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

#show producer configuration
print(producer.config)

# Get the IP address of the current machine
my_ip = socket.gethostbyname(socket.gethostname())


# Function to move coordinates within a 500m radius
def move_coordinates(coordinates, bearing, distance_meters=500):
    new_coordinates = distance(meters=distance_meters).destination((coordinates['latitude'], coordinates['longitude']), bearing)
    return {'latitude': new_coordinates.latitude, 'longitude': new_coordinates.longitude}

# Send messages to the "coordinates" topic with key 'my_ip'
topic = 'coordinates'
current_coordinates = {'latitude': 43.3150069, 'longitude': -0.3793498}
bearing = random.uniform(0, 360)  # Initial random bearing
while True:  # Send 10 messages as an example
    current_coordinates = move_coordinates(current_coordinates,bearing)
    message = {'key': my_ip, 'coordinates': current_coordinates}
    
    print(f"Sending message '{message}' to topic '{topic}'...", flush=True)
    producer.send(topic, key=my_ip, value=message)
    
    time.sleep(2)  # Wait for a minute between each send

# Close the producer
producer.close()
