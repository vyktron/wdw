import os
import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import TopicAlreadyExistsError
from kafka.admin import NewTopic, NewPartitions

# Import websocket
import websockets
import asyncio
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import PostgresDB, Location, Dad



class KafkaConsumerWrapper:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.db = None

    def create_kafka_topic(self, topic_name, partitions=1, replication_factor=1):
        # Configure the KafkaAdminClient with the Kafka bootstrap servers
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

        # Check if the topic already exists
        topic_exists = topic_name in admin_client.list_topics()
        if topic_exists:
            print(f"Topic '{topic_name}' already exists.")
            return

        # Create a NewTopic object
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replication_factor
        )

        # Create the topic
        try:
            admin_client.create_topics(new_topics=[new_topic])
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")
        
        # Create 10 partitions
        admin_client.create_partitions(topic_partitions={"coordinates": NewPartitions(total_count=10)})

    def connect(self):
        print("Connecting to Kafka...", flush=True)

        attempts = 1
        # Create a Kafka consumer
        while attempts < 4:
            try:
                self.consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)
                break
            except:
                print(f"Attempt {attempts}/3: Kafka not ready, new attempt in 10s...", flush=True)
                time.sleep(10)
                attempts += 1

        if attempts == 4:
            print("Kafka not ready, exiting...", flush=True)
            exit(1)

        print("Connected to Kafka.", flush=True)

        # Connect to the database
        print("Connecting to the database...", flush=True)
        self.db = PostgresDB(os.environ.get('DATABASE_URL'))
        print("Connected to the database.", flush=True)
    
    def push_data_to_db(self, message : dict) -> int:
        """
        Push the message to the database (and the dad if the IP address is new)

        Parameters
        ----------
        message : dict
            The message to push, containing the latitude and longitude, the dad IP address and name

        Returns
        -------
        int
            The dad id
        """

        # Get the dad from the database
        id, dad = self.db.get_dad_by_ip(message['ip'])
        if dad is None:
            # If the dad is not in the database, add it
            dad_ = Dad(ip=message['ip'], name=message['name'], latitude=message['latitude'], longitude=message['longitude'])
            id = self.db.insert_data(dad_)
        # Add the location to the database
        location = Location(latitude=message['latitude'], longitude=message['longitude'], dad_id=id)
        self.db.insert_data(location)
        # Update the dad location (if the dad existed)
        if dad is not None:
            self.db.update_dad(id, message['latitude'], message['longitude'])
        
        return id

    async def consume_messages(self, topic_name):
        # Call the function to create the Kafka topic
        self.create_kafka_topic(topic_name)

        print("Ready to consume messages.", flush=True)

        # Subscribe to the topic
        self.consumer.subscribe([topic_name])

        # Poll for messages
        async with websockets.connect('ws://fastapi:8000/ws') as websocket:
            while True:
                message = self.consumer.poll(timeout_ms=1000)
                if message:
                    # Get the keys
                    keys = message.keys()
                    for k in keys :
                        for record in message[k] :
                            # Get the value and key and parse it into a dictionary
                            value = json.loads(record.value)
                            # Add the key to the dictionary
                            value['ip'] = record.key.decode('utf-8')
                            print(f"Received message: {value}", flush=True)
                            print(f"Partition : {record.partition}", flush=True)
                            # Push the data to the database
                            dad_id = self.push_data_to_db(value)
                            value['dad_id'] = dad_id
                            await websocket.send(json.dumps(value))
                else:
                    await websocket.send("ping")
                await websocket.recv()

async def main():
    # Replace 'your_topic_name' with the desired topic name
    topic_name = 'coordinates'

    # Get the bootstrap servers from the environment variable
    bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

    kafka_consumer = KafkaConsumerWrapper(bootstrap_servers)
    kafka_consumer.connect()
    await kafka_consumer.consume_messages(topic_name)

if __name__ == "__main__":
    asyncio.run(main())

    