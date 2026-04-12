import time
import adafruit_dht
import board
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 🔐 Firebase
cred = credentials.Certificate("PI5.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# 🌡️ Sensor (DHT22 no GPIO4)
sensor = adafruit_dht.DHT22(board.D4)

print("Iniciando envio de dados...")

while True:
    try:
        temperatura = sensor.temperature
        umidade = sensor.humidity

        if temperatura is not None and umidade is not None:
            print(f"Temp: {temperatura} | Umidade: {umidade}")

            db.collection("leituras").add({
                "temperatura": float(temperatura),
                "umidade": float(umidade),
                "timestamp": datetime.utcnow()
            })

            print("Enviado para Firebase!")

        time.sleep(10)  # evita estourar quota

    except Exception as e:
        print("Erro:", e)
        time.sleep(5)
