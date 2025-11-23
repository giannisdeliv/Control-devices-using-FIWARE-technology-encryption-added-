from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import base64
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

                                     # Κλειδιά (πρέπει να είναι ίδια με Node-RED και το υπόλοιπο σύστημα)
AES_KEY = b'ThisIsA16ByteKey'        # 16 bytes (AES-128)
HMAC_KEY = b'SecretHMACKey1234'      # για HMAC

#Ρύθμιση GPIO
LED_PIN = 17                         #Physical PIN 11
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

app = Flask(__name__)

def decrypt_and_verify(iv_b64, ciphertext_b64, hmac_hex):
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    #HMAC validation
    hmac_calc = hmac.new(HMAC_KEY, iv + ciphertext, hashlib.sha256).hexdigest()        #HMAC έλεγχος, αποκρυπτογράφηση ΑΕS και αφαίρεση padding
    if not hmac.compare_digest(hmac_calc, hmac_hex):
        raise ValueError("Invalid HMAC")

    #Decrypt AES
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()

@app.route('/led', methods=['POST'])
def led_control():
    try:
        data = request.get_json()
        if not all(k in data for k in ("iv", "ciphertext", "hmac")):
            return jsonify({"error": "Missing fields"}), 400

        # Αποκρυπτογράφηση
        decrypted_json = decrypt_and_verify(data["iv"], data["ciphertext"], data["hmac"])
        print("Decrypted JSON:", decrypted_json)

        import json
        parsed = json.loads(decrypted_json)
        status = parsed.get("status", "").upper()

        if status == "ON":
            GPIO.output(LED_PIN, GPIO.HIGH)
            return jsonify({"message": "LED turned ON"}), 200                # Ανάβει ή σβήνει το LED ανάλογα το αποκρυπτογραφημένο μήνυμα και την temp που ορίσαμε
        elif status == "OFF":
            GPIO.output(LED_PIN, GPIO.LOW)
            return jsonify({"message": "LED turned OFF"}), 200
        else:
            return jsonify({"error": "Invalid status"}), 400

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 400                 #Τυπικός έλεγχος λειτουργίας, επιστρέφει 200 OK αν όλα πήγαν καλά, αλλιώς 400 Bad Request με λόγο.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)                         #Τρέχει τοπικά στο Raspberry Pi στη θύρα 5000, και περιμένει POSTs από το Node-RED
