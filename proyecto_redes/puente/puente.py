import json
import ssl
import time
import os
import requests
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
MQTT_PORT = 8883
TOPIC = "vibration/raw"

INFLUX_URL = "http://basedatos:8086"
DATABASE = "vibraciones"

USER = os.getenv("MQTT_USER")
PASSWORD = os.getenv("MQTT_PASSWORD")


def create_database():
    while True:
        try:
            response = requests.post(
                f"{INFLUX_URL}/query",
                params={"q": f"CREATE DATABASE {DATABASE}"},
                timeout=5
            )

            if response.ok:
                print("Base de datos vibraciones disponible")
                return

        except Exception as e:
            print("Esperando InfluxDB:", e)

        time.sleep(3)


def on_connect(client, userdata, flags, reason_code, properties):
    print("Conectado a MQTT:", reason_code)
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        line = (
            f'vibration,device={data["device_id"]},state={data["state"]} '
            f'ax={data["ax"]},'
            f'ay={data["ay"]},'
            f'az={data["az"]},'
            f'frequency={data["frequency"]}'
        )

        response = requests.post(
            f"{INFLUX_URL}/write",
            params={"db": DATABASE},
            data=line,
            timeout=5
        )

        if response.status_code == 204:
            print("Guardado:", data)
        else:
            print("Error InfluxDB:", response.text)

    except Exception as e:
        print("Error:", e)


create_database()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

if USER:
    client.username_pw_set(USER, PASSWORD)

client.tls_set(
    ca_certs="/certs/ca.crt",
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, MQTT_PORT, 60)

print("Puente iniciado")

client.loop_forever()
