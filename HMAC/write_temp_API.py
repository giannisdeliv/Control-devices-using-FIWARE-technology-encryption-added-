import adafruit_dht
import board
import requests
import time
import json
import base64
import os
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

                                   # Ρύθμιση των Keys
AES_KEY = b'ThisIsA16ByteKey'      # 16 bytes=128-bit key και τα ορλιζουμε εμείς τυχαία(μη δημόσια)
HMAC_KEY = b'SecretHMACKey1234'    


dhtDevice = adafruit_dht.DHT22(board.D4)  #Σύνδεση αισθητήρα DHT22 στην GPIO 4

# Node-RED endpoint(διεύθυνση αποστολής)
NODE_RED_URL = "http://<Laptop_IP>:1880/temperature"



def encrypt_and_mac(plaintext: str):                                                    #Κρυπτογραφεί τα δεδομένα με AES-CBC
    
    iv = os.urandom(16)                                                                 
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))

    
    hmac_obj = hmac.new(HMAC_KEY, iv + ciphertext, hashlib.sha256)                      #Υπολογισμός HMAC (με βάση IV + ciphertext)
    mac = hmac_obj.hexdigest()

   
    return {                                                                            
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "hmac": mac
    }

while True:
    try:
        temperature = round(dhtDevice.temperature, 1)                             #Κάθε 5 sec, διαβάζει τιμές, τις κωδικοποιεί και τις στέλνει στο Node-Red   
        humidity = round(dhtDevice.humidity, 1)

        print(f"Temp: {temperature} °C,Humidity: {humidity} %")

        # JSON σε μορφή string
        plaintext = json.dumps({
            "temperature": temperature,
            "humidity": humidity
        })

        # Κρυπτογράφηση + MAC
        encrypted_payload = encrypt_and_mac(plaintext)

        # Αποστολή
        response = requests.post(NODE_RED_URL, json=encrypted_payload, timeout=5)
        print(f"Sent Encrypted: {encrypted_payload}, Status: {response.status_code}")

    except Exception as e:
        print(f" Error: {e}")

    time.sleep(5)
