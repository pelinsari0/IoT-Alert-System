import random
import time
from datetime import datetime

import requests

API_URL = "http://127.0.0.1:9000/api/readings"

DEVICES = [
    ("sensor-1", "living_room"),
    ("sensor-2", "bedroom"),
    ("sensor-3", "kitchen"),
]


def generate_reading(device_id: str, location: str) -> dict:
    temperature = random.uniform(20.0, 35.0)
    humidity = random.uniform(25.0, 80.0)
    motion = random.random() < 0.3  # ~30% chance

    return {
        "device_id": device_id,
        "location": location,
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "motion": motion,
    }


def main():
    print("Starting virtual sensor simulator. Press Ctrl+C to stop.")
    while True:
        for device_id, location in DEVICES:
            reading = generate_reading(device_id, location)
            try:
                resp = requests.post(API_URL, json=reading, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    alerts = data.get("alerts", [])
                    timestamp = datetime.now().isoformat(timespec="seconds")
                    if alerts:
                        print(f"[{timestamp}] ALERTS:", alerts)
                    else:
                        print(f"[{timestamp}] OK:", reading)
                else:
                    print("Server error:", resp.status_code, resp.text)
            except Exception as exc:
                print("Failed to send reading:", exc)

        time.sleep(5) 


if __name__ == "__main__":
    main()
