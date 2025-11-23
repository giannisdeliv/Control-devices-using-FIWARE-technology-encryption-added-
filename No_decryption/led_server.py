from flask import Flask, request
import RPi.GPIO as GPIO

# Ρύθμιση GPIO
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

app = Flask(__name__)

@app.route('/led', methods=['POST'])
def led_control():
    data = request.get_json()
    if not data or 'status' not in data:
        return {"message": "Missing status"}, 400

    if data['status'] == "ON":
        GPIO.output(LED_PIN, GPIO.HIGH)
        return {"message": "LED turned ON"}, 200
    elif data['status'] == "OFF":
        GPIO.output(LED_PIN, GPIO.LOW)
        return {"message": "LED turned OFF"}, 200
    else:
        return {"message": "Invalid status"}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
