import adafruit_dht
import board
import requests
import time

# Αρχικοποίηση αισθητήρα DHT22 στη GPIO 4
dhtDevice = adafruit_dht.DHT22(board.D4)

# URL Node-RED
NODE_RED_URL = "http://<Laptop_IP>:1880/temperature"

while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        print(f" Θερμοκρασία: {temperature:.1f} °C, Υγρασία: {humidity:.1f}%")

        # Αποστολή σωστού JSON με json=payload
        payload = {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1)
        }

        response = requests.post(NODE_RED_URL, json=payload, timeout=5)
        print(f" Αποστολή: {payload}, Κωδικός: {response.status_code}")

    except Exception as e:
        print(f"Σφάλμα: {e}")

    time.sleep(5)
