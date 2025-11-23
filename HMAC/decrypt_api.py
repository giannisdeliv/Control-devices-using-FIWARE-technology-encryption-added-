from flask import Flask, request, jsonify
import base64
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

AES_KEY = b'ThisIsA16ByteKey'                        #Το AES_KEY και HMAC_KEY πρέπει να είναι ίδια με αυτά που χρησιμοποιούνται στο write_temp_API.py
HMAC_KEY = b'SecretHMACKey1234'

def decrypt_payload(iv_b64, ciphertext_b64, hmac_hex):
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    # HMAC Verification
    h = hmac.new(HMAC_KEY, iv + ciphertext, hashlib.sha256).hexdigest()          #Επαλήθευση HMAC (για ακεραιότητα),αποκρυπτογράφηση με AES-CBC,αφαίρεση padding,επιστροφή καθαρού string
    if not hmac.compare_digest(h, hmac_hex):
        raise ValueError("Invalid HMAC")

    # AES-CBC Decryption
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()

@app.route('/decrypt_and_decide', methods=['POST'])                          #Εδώ ορίζεται το route που καλεί ο Node-RED με HTTP POST
def decrypt_and_decide():
    try:
        data = request.get_json()                                              
        if not all(k in data for k in ("iv", "ciphertext", "hmac")):         #Αν λείπει κάποιο βασικό πεδίο(tag), επιστρέφει σφάλμα
            return jsonify({"error": "Missing fields"}), 400

        decrypted_json = decrypt_payload(data["iv"], data["ciphertext"], data["hmac"])
        print("Decrypted:", decrypted_json)                                                 #Τυπώνει το decrypted json string και παίρνει απόφαση

        import json
        values = json.loads(decrypted_json)
        temp = float(values.get("temperature", 0))
        status = "ON" if temp > 15 else "OFF"                    #Έλεγχος θερμοκρασίας, το ορίζουμε εμείς

        return jsonify({"status": status}), 200                  #Επιστρέφεται πίσω στον Node-RED,καλεί το encrypt API και στέλνει το encrypted status πίσω στο Raspberry Pi

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)                         #Ανοίγει τον server στη θύρα 5050 
