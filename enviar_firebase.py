import adafruit_dht
import board
import time
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 🔐 Inicializar Firebase
cred = credentials.Certificate("PI5.json")  # <-- coloque o nome correto aqui
firebase_admin.initialize_app(cred)

db = firestore.client()

# 🌡️ Sensor
sensor = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperatura = sensor.temperature
        umidade = sensor.humidity

        if temperatura is not None and umidade is not None:
            print(f"Temp: {temperatura:.1f}°C  Umidade: {umidade:.1f}%")

            db.collection("leituras").add({
                "temperatura": temperatura,
                "umidade": umidade,
                "timestamp": datetime.now()
            })

            print("✅ Enviado para o Firebase!")

    except RuntimeError:
        print("Erro na leitura, tentando novamente...")

    time.sleep(10)
