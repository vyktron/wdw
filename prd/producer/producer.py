import os
from kafka import KafkaProducer

# Get the bootstrap server from the environment variable
bootstrap_servers = os.environ.get('KAFKA_REST_BOOTSTRAP_SERVERS')

# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# Send messages to the "coordinates" topic
topic = 'coordinates'
messages = ['message1', 'message2', 'message3']



for message in messages:
    print(f"Sending message '{message}' to topic '{topic}'...")
    producer.send(topic, message.encode('utf-8'))

# Close the producer
producer.close()
