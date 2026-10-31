import json
import random
import time
import ssl
import os

import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 8883
TOPIC = "vibration/raw"

USER = os.getenv("MQTT_USER")
PASSWORD = os.getenv("MQTT_PASSWORD")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

if USER:
    client.username_pw_set(USER, PASSWORD)

client.tls_set(
    ca_certs="/certs/ca.crt",
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

client.connect(BROKER, PORT, 60)
client.loop_start()

print("Simulador iniciado")

while True:

    estado = random.choice([
        "normal",
        "parkinson",
        "taladro",
        "perforadora"
    ])

    if estado == "normal":
        frecuencia = random.uniform(0.5, 2)

    elif estado == "parkinson":
        frecuencia = random.uniform(4, 6)

    elif estado == "taladro":
        frecuencia = random.uniform(35, 55)

    else:
        frecuencia = random.uniform(60, 90)

    dato = {
        "device_id": "esp32_sim_01",
        "ax": round(random.uniform(-3, 3), 3),
        "ay": round(random.uniform(-3, 3), 3),
        "az": round(random.uniform(7, 11), 3),
        "frequency": round(frecuencia, 2),
        "state": estado
    }

    client.publish(
        TOPIC,
        json.dumps(dato)
    )

    print(dato)

    time.sleep(1)
