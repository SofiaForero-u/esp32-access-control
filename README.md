# Proyecto ESP32 + RFID + Reconocimiento Facial

Este sistema permite controlar el acceso mediante un lector RFID y verificación facial usando ESP32, ESP32-CAM y un servidor Flask con OpenCV.

## Componentes
- ESP32 + MicroPython
- Lector RFID RC522
- ESP32-CAM
- Servidor Flask en PC
- Módulo relé o servo

## Flujo
1. Escanea tarjeta RFID.
2. Si es válida, toma una foto desde ESP32-CAM.
3. Envía la foto al servidor.
4. Si el rostro es válido, se activa la cerradura.

## Instalación
- En ESP32 usar Thonny para subir main.py y mfrc522.py
- En ESP32-CAM usar Arduino IDE para subir esp32cam_upload.ino y mande la foto al servidor
- En tu PC: instalar Flask, OpenCV y ejecutar server.py
