from flask import Flask, request, jsonify
import base64
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import json

app = Flask(__name__)

AES_KEY = b'ThisIsA16ByteKey'                  # Πρέπει να είναι ίδια με τα υπόλοιπα συστήματα (Raspberry Pi & decrypt API)
HMAC_KEY = b'SecretHMACKey1234'

@app.route('/encrypt_status', methods=['POST'])  # Το endpoint που καλεί ο Node-RED μετά την απόφαση status = ON/OFF
def encrypt_status():
    try:
        data = request.get_json()
        if 'status' not in data:
            return jsonify({"error": "Missing 'status' field"}), 400        # Επιστρέφει σφάλμα αν λείπει το status

        plaintext = json.dumps({ "status": data["status"] })
        iv = os.urandom(16)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        mac = hmac.new(HMAC_KEY, iv + ciphertext, hashlib.sha256).hexdigest()     #Κρυπτογραφεί με AES και δημιουργεί HMAC από το IV + ciphertext

        return jsonify({
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),                      # Το επιστρέφει σε συμβατό JSON format προς Node-RED
            "hmac": mac
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500                            #Το API ακούει στη θύρα 5051

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051)
