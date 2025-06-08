from machine import Pin, PWM, SPI
from mfrc522 import MFRC522
import network
import time
import urequests

servo = PWM(Pin(13), freq=50)
def lock(): servo.duty(40)
def unlock(): servo.duty(115)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("TuSSID", "TuPassword")  # Cambia por tu red
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado:", wlan.ifconfig())

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rdr = MFRC522(spi=spi, gpio_rst=Pin(22), gpio_cs=Pin(5))
uid_autorizado = [0xDE, 0xAD, 0xBE, 0xEF]  # Cambia por el UID de tu tarjeta

conectar_wifi()
lock()
while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            print("UID detectado:", raw_uid)
            if raw_uid == uid_autorizado:
                print("Enviando solicitud al servidor...")
                res = urequests.get("http://<IP_SERVIDOR>:5000/verificar")  # Cambia <IP_SERVIDOR>
                if res.text == "OK":
                    print("✅ Acceso concedido")
                    unlock()
                    time.sleep(5)
                    lock()
                else:
                    print("❌ Rostro no reconocido")
            else:
                print("Tarjeta no autorizada")
    time.sleep(1)
