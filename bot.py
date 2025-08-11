# bot.py - Bot MUY SIMPLE para pruebas
from flask import Flask, request
import requests

app = Flask(__name__)

# === CONFIGURACIÓN (cámbialo por tu token real) ===
TOKEN = "7985103761:AAEcCdKMmchwm8rkXyLP0eQ5VvLJDNpfLBE"

# === RUTA DE PRUEBA ===
@app.route('/')
def home():
    return "Bot funcionando. Usa /webhook", 200

# === WEBHOOK DE TELEGRAM ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("🔹 Datos recibidos:", data)  # Ver en logs de Render

        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message']['text']

            if text == '/start':
                print(f"✅ /start recibido de {chat_id}")
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": "Hola! El bot está funcionando."}
                )
    except Exception as e:
        print("❌ Error:", e)
    return 'ok', 200
