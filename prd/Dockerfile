
FROM python:3.8

WORKDIR /producer

RUN pip install kafka-python geopy

COPY . /producer

# Add your application code here

CMD [ "python", "producer/producer.py" ]
