import os
import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import TopicAlreadyExistsError
from kafka.admin import NewTopic

class KafkaConsumer:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None

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

    def connect(self):
        print("Connecting to Kafka...", flush=True)

        attempts = 1
        # Create a Kafka consumer
        while attempts < 4:
            try:
                self.consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)
                break
            except:
                print(f"Attempt {attempts}/3: Kafka not ready, new attempt in 5s...", flush=True)
                time.sleep(5)
                attempts += 1

        if attempts == 4:
            print("Kafka not ready, exiting...", flush=True)
            exit(1)

        print("Connected to Kafka.", flush=True)

    def consume_messages(self, topic_name):
        # Call the function to create the Kafka topic
        self.create_kafka_topic(topic_name)

        print("Ready to consume messages.", flush=True)

        # Subscribe to the topic
        self.consumer.subscribe([topic_name])

        # Poll for messages
        while True:
            message = self.consumer.poll(timeout_ms=1000)
            if message:
                print(message, flush=True)
            time.sleep(1)

if __name__ == "__main__":
    # Replace 'your_topic_name' with the desired topic name
    topic_name = 'coordinates'

    # Get the bootstrap servers from the environment variable
    bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

    kafka_consumer = KafkaConsumerWrapper(bootstrap_servers)
    kafka_consumer.connect()
    kafka_consumer.consume_messages(topic_name)

    