# IoT Sensor Data Pipeline: MQTT, PostgreSQL, and Python on Docker

## Overview
The use of containers has transformed the way applications are developed, deployed, and maintained, allowing services to run in isolation and facilitating their configuration across different environments. Docker is an open-source platform that enables the creation, execution, and management of containers, offering a lightweight and flexible alternative for deploying applications without the need for full virtual machines. Its operation relies on Linux kernel features, such as control groups (cgroups) and namespaces, which allow system resource management and process isolation within each container.

In this practice, these concepts are applied by implementing a data pipeline for an Internet of Things (IoT) system[cite: 1]. Three services are configured and connected through a virtual bridge network: an Eclipse Mosquitto MQTT broker, a PostgreSQL 18 database, and a client developed in Python[cite: 1]. These services allow receiving temperature data via the MQTT protocol—based on a publish-subscribe model—and storing it in the database using the Paho-MQTT and psycopg2 libraries[cite: 1].

## System Architecture
All services communicate over an isolated Docker user-defined bridge network (`appnet`), with no host port exposure except the broker for external publishers[cite: 1, 2].
*   **Mosquitto MQTT Broker:** Runs with anonymous login disabled, utilizing a hashed password file for authentication[cite: 1, 2].
*   **PostgreSQL 18 Database:** Stores sensor readings with credentials loaded from an `.env` file[cite: 1, 4]. Data state is persisted to a host bind-mount (`/database/pgdata`) using the major-version-aware layout[cite: 1, 4].
*   **Python Client:** A containerized Paho-MQTT client that subscribes to the `sensors/temp` topic, parses incoming JSON payloads (e.g., `{"temp": 25.5}`), and inserts the readings into auto-created Postgres tables[cite: 1, 6]. It includes a standard-library dependency waiter (`wait_for.py`) to ensure ordered startup[cite: 1, 7].

## Prerequisites
*   Docker Engine $\ge24.x$ installed and running[cite: 1].
*   Docker CLI access without sudo[cite: 1].

## Project Structure
```text
project-root/
├── .env
├── broker/
│   ├── config/
│   │   ├── mosquitto.conf
│   │   └── passwd
│   ├── data/
│   └── log/
├── database/
│   └── pgdata/
└── client/
    ├── Dockerfile
    ├── requirements.txt
    └── src/
        ├── client.py
        └── wait_for.py
