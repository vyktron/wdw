
# Use a Python base image
FROM python:3.8

# Set the working directory
WORKDIR /consumer

# Ugrade pip
RUN pip install --upgrade pip
# Install the kafka-python library
RUN pip install kafka-python pydantic websockets psycopg2-binary

# Copy your application code to the container
COPY . /consumer
# Copy the "db" folder that is in the parent directory to the container
COPY ../db /db

# Set the entrypoint command
CMD ["python", "consumer/consumer.py"]
