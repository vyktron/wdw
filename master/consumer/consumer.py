import os
import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import TopicAlreadyExistsError
from kafka.admin import NewTopic

def create_kafka_topic(bootstrap_servers, topic_name, partitions=1, replication_factor=1):
    # Configure the KafkaAdminClient with the Kafka bootstrap servers
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

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

if __name__ == "__main__":

    # Replace 'your_topic_name' with the desired topic name
    topic_name = 'coordinates'

    print("Creating Kafka topic...")
    
    # Wait for Kafka to be up and running
    time.sleep(30)

    # Get the bootstrap servers from the environment variable
    bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

    # Create a Kafka consumer
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)

    # Call the function to create the Kafka topic
    create_kafka_topic(bootstrap_servers, topic_name)
