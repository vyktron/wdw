
FROM python:3.8

WORKDIR /producer

COPY . /producer

RUN pip install kafka-python

# Add your application code here

CMD [ "python", "producer/producer.py" ]
