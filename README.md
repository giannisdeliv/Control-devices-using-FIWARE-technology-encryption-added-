# Control devices using FIWARE technology (basic + HMAC-secured versions)

This repository contains the implementation of an end-to-end IoT architecture using a **Raspberry Pi 4**, **Node-RED** and
the **FIWARE Orion Context Broker**.

The system is implemented in two main versions:

- `No_decryption/` → basic version (plain HTTP JSON, no encryption)
- `HMAC/` → secure version (AES encryption + HMAC authentication)

The core idea is:

1. Read temperature (and humidity) from a DHT22 sensor on a Raspberry Pi  
2. Send measurements to Node-RED via HTTP  
3. Visualize them on a web dashboard  
4. Decide whether an LED should be ON/OFF (based on temperature threshold)  
5. Control an LED connected to the Raspberry Pi  
6. Update a FIWARE Orion entity with the latest context  
7. In the secure version, protect messages between Raspberry Pi and Node-RED
   using AES + HMAC.

---

## 1. Repository structure

```text
.
├── HMAC/                   # Secure version (AES + HMAC)
├── No_decryption/          # Basic version (no encryption)
├── HMAC.zip                # Same content as HMAC/ (kept only as archive)
├── No_decryption.zip       # Same content as No_decryption/ (archive)
└── docker-compose.yml      # FIWARE stack (Orion + MongoDB + Node-RED)
