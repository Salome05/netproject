import os
import json
import ssl
import time

import psycopg2
import paho.mqtt.client as mqtt


# =========================
# MQTT CONFIGURATION
# =========================

MQTT_HOST = os.environ.get("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "8883"))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "sensors/temp")

MQTT_CA_CERT = os.environ.get(
    "MQTT_CA_CERT",
    "/certs/ca.crt"
)


# =========================
# POSTGRES CONFIGURATION
# =========================

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "BD1")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")


# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[mqtt] connected rc={reason_code}")

    client.subscribe(MQTT_TOPIC)

    print(f"[mqtt] subscribed to {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        print(f"[mqtt] {msg.topic} -> {payload}")

    except json.JSONDecodeError:
        print("[mqtt error] invalid JSON")
        return

    table_name = msg.topic.strip("/").replace("/", "_")

    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )

        conn.autocommit = True

        cur = conn.cursor()

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                id SERIAL PRIMARY KEY,
                temp DOUBLE PRECISION,
                received_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )

        cur.execute(
            f"""
            INSERT INTO "{table_name}" (temp)
            VALUES (%s);
            """,
            (
                payload.get("temp"),
            )
        )

        print(
            f"[db] inserted into {table_name}: "
            f"{payload.get('temp')}"
        )

        cur.close()
        conn.close()

    except Exception as e:
        print(f"[db error] {e}")


# =========================
# MAIN
# =========================

def main():

    client = mqtt.Client(
        client_id="pg-client",
        protocol=mqtt.MQTTv5
    )

    client.username_pw_set(
        MQTT_USER,
        MQTT_PASSWORD
    )

    # TLS configuration
    client.tls_set(
        ca_certs=MQTT_CA_CERT,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )

    client.on_connect = on_connect
    client.on_message = on_message

    while True:

        try:

            print(
                f"[mqtt] connecting to "
                f"{MQTT_HOST}:{MQTT_PORT} using TLS"
            )

            client.connect(
                MQTT_HOST,
                MQTT_PORT,
                keepalive=60
            )

            client.loop_forever(
                retry_first_connection=True
            )

        except Exception as e:

            print(
                f"[connect error] {e}, "
                f"retrying in 5s..."
            )

            time.sleep(5)


if __name__ == "__main__":
    main()
