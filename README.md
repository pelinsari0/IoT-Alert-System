# IoT Data Management & Alert System Simulation

This project simulates an offline IoT data pipeline using **FastAPI** and **SQLite**.

Virtual sensors generate temperature, humidity, and motion data. The backend stores
readings in a local SQLite database and triggers threshold-based alerts, which are
logged to the console and to a log file.

## Tech Stack

- Python, FastAPI
- SQLite + SQLAlchemy
- Requests (for sensor simulator)

## Setup

```bash

# Windows:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Linux/macOS:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


# Uvicorn:
uvicorn app.main:app --reload --host 127.0.0.1 --port 9000

# Running the virtual IoT sensors:
python sensors/sensors_simulator.py

# Running GUI user interface:
python -m gui_dashboard.main