import os
import platform
import psutil
import requests
import json
import logging
import time

API_HOST = os.getenv("API_HOST")

logging.basicConfig(level=logging.INFO)

def collect_system_info():
    return {
        "processor": platform.processor(),
        "processes": [p.info for p in psutil.process_iter(['pid', 'name'])],
        "users": [user.name for user in psutil.users()],
        "os_name": platform.system(),
        "os_version": platform.version()
    }

if __name__ == '__main__':
    # Esperar unos segundos para asegurarse de que la API esté lista
    time.sleep(10)
    try:
        data = collect_system_info()
        response = requests.post(f"{API_HOST}/collect", json=data)
        #response = requests.post(f"http://localhost:5012/collect", json=data) # USAR SOLO CUANDO SE CORRE EL SCRIPT LOCAL SIN DOCKER
        if response.status_code == 201:
            logging.info("Data sent successfully!")
        else:
            logging.error(f"Failed to send data: {response.status_code}, {response.text}")
    except Exception as e:
        logging.error(f"Error: {e}")