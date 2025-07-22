# FastAPI-Celery-Redis-Flower

A FastAPI ML application using sentence transformers, Celery, Redis and Flower.

[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#fastapi">FastAPI</a></li>
    <li><a href="#celery">Celery</a></li>
    <li><a href="#redis">Redis</a></li>
    <li><a href="#flower">Flower</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This project utilizes FastAPI alongside Celery for asynchronous task execution, Redis for storage and as a message broker between Celery and FastAPI, and Flower for real-time monitoring of Celery. This tech stack was used to efficiently generate and serve embeddings for text data. With FastAPI's high-performance framework and Celery's distributed task processing, the application can scale efficiently to process a large number of tasks.

### Built With

* [FastAPI](https://fastapi.tiangolo.com/)
* [Celery](https://docs.celeryq.dev/en/stable/index.html#)
* [Redis](https://redis.io/)
* [Flower](https://flower.readthedocs.io/en/latest/)

## Getting Started

The application is build with docker-compose to create the various microservices. These include the FastAPI application itself, the Redis database and the Celery application. To build the Dockerfile for both FastAPI and Celery, use the following command:

```bash
docker-compose build
```

The Redis Docker alpine image is taken directly from DockerHub. To run all the necessary containers for the application, use the following command:

```bash
docker-compose up
```

FastAPI can be accessed from ```0.0.0.0:8080``` and a SwaggerUI can be accessed fromt the ```/docs``` route. The Flower UI can be accessed from ```0.0.0.0:5556``` where the user can monitor the Celery cluster.
The following environment variables are also needed in a ```.env``` file.

```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_HOST=redis://redis:6379/0
```

## FastAPI

FastAPI is a modern web framework for building APIs with Python, emphasizing performance, type hints, and automatic documentation generation. It leverages Python's type annotations for input validation and code generation, resulting in high-speed API development with minimal boilerplate. FastAPI offers built-in support for asynchronous programming, making it an ideal choice for scalable and efficient backend development.


## Celery

Celery is a distributed task queue framework for processing asynchronous tasks in Python. It enables the execution of tasks asynchronously, allowing for the scalable and efficient handling of background jobs. With support for various brokers like Redis, RabbitMQ, and others, Celery facilitates seamless communication between components of a distributed system. Celery's flexible and robust architecture makes it well-suited for handling tasks ranging from simple to complex in various applications.

## Redis

Redis is an open-source, in-memory data structure store used as a database, cache, and message broker. It provides high performance, low latency access to data by storing it in-memory. Redis supports various data structures like strings, hashes, lists, sets, and more, making it versatile for different use cases. Its simplicity and scalability make it a popular choice for real-time applications, caching layers, and distributed systems.

## Flower

Flower is an open-source web-based tool for monitoring and managing Celery clusters. It provides real-time monitoring of task progress, worker status, and resource usage. Flower offers insights into task execution, enabling efficient management and debugging of distributed Celery systems. Flower supports authentication, task filtering, and various customizable features for comprehensive Celery cluster management.

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-white.svg?
[linkedin-url]: https://linkedin.com/in/stelios-giannikis
