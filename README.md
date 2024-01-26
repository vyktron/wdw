# Where Dad Went?

Dockerized GPS Tracker microservices using Kafka, FastAPI and PostgreSQL

## Origins

A picture is worth a thousand words
<img
  src="/img/why-wdw.png"
  alt="Alt text"
  style="display: inline-block; margin: 0 auto; max-width: 300px">

## Architecture

The architecture is called "microservice", which means that services such as the database, the frontend, etc. are distributed in different docker containers (as minimal as possible).

In our case, the machines in the cluster can have two distinct roles: "Master" and "Producer". Note that the master node may itself be distributed across several machines (one machine may host the Kafka broker, another may host the web application...).

<img
  src="/img/architecture.png"
  alt="Alt text"
  title="Architecture"
  style="display: inline-block; margin: 0 auto; max-width: 300px">

### Producers

The producer knows the master's IP address and sends its GPS data via the Kafka broker.

To mimic a person on the move, when the producer node is started, a random GPS point is chosen (from a list of French cities) and starts moving to a nearby city (not the nearest, but not too far away). 
The producer sends its data to a subject named `coordinates` and uses its IP address as a key to balance the load between the broker's available partitions.

### Consumer

The consumer has to role to consumer the messages and send it to the FastAPI container to be visualized by the user and to the PostgresSQL container to be saved on disk (and as a backup in case of Kafka failure).

### WebApp

The webapp is based on FastAPI and a Uvicorn server and has the role to render the positions on a map in real-time. When started the PostgresSQL is called to access last data saved and render all known producers. If the consumer sends messages, FastAPI will receive it and send it to the frontend to be rendered.

### Database

The database is a docker image of PostgreSQL. The consumed messages are saved in the database on a shared volume following this structure :

<img
  src="/img/db.png"
  alt="Alt text"
  title="Tables"
  style="display: inline-block; margin: 0 auto; max-width: 300px">
