import os
from kafka import KafkaProducer
import json
import random
import time
import socket
import random
from geopy.distance import distance
import math

class KafkaProducerWrapper:
    def __init__(self):
        # Get the bootstrap server from the environment variable
        bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')
        # Create a Kafka producer
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      key_serializer=str.encode,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))

        # Get the IP address of the current machine
        self.host_ip = socket.gethostbyname(socket.gethostname())

        # Set seed for random with the IP address
        random.seed(self.host_ip)
        # Get a random name
        self.name = random.choice(["Jacques", "Jean", "Paul", "François", "Pierre", "Jean-Pierre", "Jean-François", 
                                   "Charles", "André", "René", "Henri", "Michel", "Louis", "Georges", "Marcel", "Alain",
                                   "Bernard", "Robert", "Roger", "Daniel", "Jean-Claude", "Jean-Louis", "Jean-Marie",
                                   "Claude", "Christian", "Claude", "Guy", "Philippe", "Gérard", "Jean-Paul"])
        

        # Get the cities coordinates in the json file "cities.json"
        print("Loading cities coordinates...", flush=True)
        with open('producer/cities.json') as f:
            list_cities = json.load(f)["cities"]
            self.cities = [{'latitude': city['latitude'], 'longitude': city['longitude']} for city in list_cities]
        
        # Get the starting point by choosing a random city
        city = random.choice(self.cities) ; self.coordinates = {'latitude': float(city['latitude']), 'longitude': float(city['longitude'])}
        # Define the target
        self.target = self.define_target()
        
    def define_target(self):
        # Get the 20-50 closest cities (to avoid being too close or too far targets)
        closest_cities = sorted(self.cities, key=lambda city: distance((self.coordinates['latitude'], self.coordinates['longitude']), (city['latitude'], city['longitude'])).meters)[20:50]
        # Choose a random city among the 5 closest
        city = random.choice(closest_cities)
        return {'latitude': float(city['latitude']), 'longitude': float(city['longitude'])}
    
    def get_speed(self):
        # Speed depends on the distance between the current position and the target
        distance_to_target = distance((self.coordinates['latitude'], self.coordinates['longitude']), (self.target['latitude'], self.target['longitude'])).meters
        if distance_to_target >= 5e4 : # If the distance is greater than 50km
            return (130/3.6) # 130km/h
        else :
            return (130*distance_to_target/5e4 + 50)/3.6 # 50km/h at 0m, 130km/h at 50km
    
    def calculate_bearing(self):
        # Calculate the bearing to the target
        delta_longitude = self.target['longitude'] - self.coordinates['longitude']
        x = math.cos(math.radians(self.target['latitude'])) * math.sin(math.radians(delta_longitude))
        y = math.cos(math.radians(self.coordinates['latitude'])) * math.sin(math.radians(self.target['latitude'])) - math.sin(math.radians(self.coordinates['latitude'])) * math.cos(math.radians(self.target['latitude'])) * math.cos(math.radians(delta_longitude))
        bearing = math.atan2(x, y)

        # Add a random noise to the bearing
        bearing += random.uniform(-0.3, 0.3) # 0.3 rad = 17°
        
        return  (math.degrees(bearing) + 360) % 360 # Convert to degrees and keep the value between 0 and 360 

    # Function to move coordinates within a 500m radius
    def move_coordinates(self):
        # Calculate speed and bearing
        speed = self.get_speed()
        
        bearing = self.calculate_bearing()
        # Move the coordinates
        new_coordinates = distance(meters=speed).destination((self.coordinates['latitude'], self.coordinates['longitude']), bearing)

        # If the speed is below 55km/h, change the target (it means being in a city at a around 2km from the target)
        if speed < 55/3.6 :
            self.target = self.define_target()

        return {'latitude': new_coordinates.latitude, 'longitude': new_coordinates.longitude}

    def send_position(self):
        # Send messages to the "coordinates" topic with key 'host_ip'
        topic = 'coordinates'

        while True:
            # Move the coordinates
            self.coordinates = self.move_coordinates()
            message = {'name': self.name, 'latitude': self.coordinates['latitude'], 'longitude': self.coordinates['longitude']}
            print( f"Sending message: {message}", flush=True)
            self.producer.send(topic, key=self.host_ip, value=message)
            time.sleep(1)  # Wait for a seconde between each message

    def close_producer(self):
        # Close the producer
        self.producer.close()

# Create an instance of the Producer class
if __name__ == "__main__":
    producer = KafkaProducerWrapper()
    producer.send_position()
    producer.close_producer()
