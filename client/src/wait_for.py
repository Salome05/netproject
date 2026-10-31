import os
import socket
import time
import sys


DEPS = [
    (
        "postgres",
        os.environ.get("POSTGRES_HOST", "postgres"),
        int(os.environ.get("POSTGRES_PORT", "5432"))
    ),
    (
        "mosquitto",
        os.environ.get("MQTT_HOST", "mosquitto"),
        int(os.environ.get("MQTT_PORT", "1883"))
    ),
]

TIMEOUT = int(os.environ.get("WAIT_TIMEOUT", "120"))
INTERVAL = int(os.environ.get("WAIT_INTERVAL", "2"))


def reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def main():
    deadline = time.time() + TIMEOUT

    while time.time() < deadline:
        still_down = []

        for name, host, port in DEPS:
            if not reachable(host, port):
                still_down.append(name)

        if not still_down:
            print("[wait] all dependencies reachable")
            break

        print(f"[wait] waiting on: {', '.join(still_down)}")
        time.sleep(INTERVAL)

    else:
        print(f"[wait] TIMEOUT — still down: {still_down}")
        sys.exit(1)

    os.execvp("python", ["python", "-u", "client.py"])


if __name__ == "__main__":
    main()
