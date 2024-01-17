import os
from kafka import KafkaProducer
import json
import random
import time
import socket
import math
from geopy.distance import distance

class KafkaProducer:
    def __init__(self):
        # Get the bootstrap server from the environment variable
        bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

        # Create a Kafka producer
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      key_serializer=str.encode,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))

        # Get the IP address of the current machine
        self.host_ip = socket.gethostbyname(socket.gethostname())

    # Function to move coordinates within a 500m radius
    def move_coordinates(self, coordinates, bearing, distance_meters=500):
        new_coordinates = distance(meters=distance_meters).destination((coordinates['latitude'], coordinates['longitude']), bearing)
        return {'latitude': new_coordinates.latitude, 'longitude': new_coordinates.longitude}

    def send_position(self):
        # Send messages to the "coordinates" topic with key 'host_ip'
        topic = 'coordinates'
        current_coordinates = {'latitude': 43.3150069, 'longitude': -0.3793498}
        bearing = random.uniform(0, 360)  # Initial random bearing
        while True:
            current_coordinates = self.move_coordinates(current_coordinates, bearing)
            message = {'key': self.host_ip, 'coordinates': current_coordinates}

            print(f"Sending message '{message}' to topic '{topic}'...", flush=True)
            self.producer.send(topic, key=self.host_ip, value=message)

            time.sleep(1)  # Wait for a seconde between each send

    def close_producer(self):
        # Close the producer
        self.producer.close()

# Create an instance of the Producer class
if __name__ == "__main__":
    producer = KafkaProducer()
    producer.send_position()
    producer.close_producer()
