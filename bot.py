# bot.py
from flask import Flask, request
import logging
import paramiko
import json

# === CONFIGURACIÓN (usa variables de entorno en Render) ===
TOKEN = "7985103761:AAEcCdKMmchwm8rkXyLP0eQ5VvLJDNpfLBE"  # ← En Render: añade como secreto
VPS_IP = "102.129.137.108"
VPS_USER = "root"
VPS_PASS = "Tteam2215"

# URL del webhook (Render te dará esta URL)
# Ej: https://tu-bot.onrender.com/webhook

app = Flask(__name__)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = app.logger

# === CONEXIÓN SSH AL VPS ===
def ssh_command(cmd):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=10)
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode('utf-8') or "✅ Comando ejecutado."
        error = stderr.read().decode('utf-8')
        client.close()
        return f"{output}\n{error}".strip() if error else output.strip()
    except Exception as e:
        return f"❌ Error SSH: {str(e)}"

# === MENÚ DE BOTONES (para devolver en Telegram) ===
keyboard = {
    "keyboard": [
        [{"text": "🔐 Generar Test"}],
        [{"text": "📊 Usuarios Online"}, {"text": "⚡ SpeedTest"}],
        [{"text": "🔄 Reiniciar Servicios"}]
    ],
    "resize_keyboard": True
}

# === RUTA DEL WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")

        # Extraer datos del mensaje
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        # Respuesta base
        reply = {
            "chat_id": chat_id,
            "text": "🤖 Usa el menú:",
            "reply_markup": keyboard
        }

        # Ejecutar comandos
        if text == "/start":
            reply["text"] = "👋 ¡Hola! Usa el menú para gestionar tu VPS."

        elif text == "🔐 Generar Test":
            reply["text"] = "⏳ Generando usuario de prueba..."
            result = ssh_command("criarteste")
            reply["text"] = f"<b>Usuario de prueba creado:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        elif text == "📊 Usuarios Online":
            reply["text"] = "🔍 Cargando usuarios online..."
            result = ssh_command("sshmonitor")
            reply["text"] = f"<b>Usuarios Online:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        elif text == "⚡ SpeedTest":
            reply["text"] = "📡 Ejecutando speedtest..."
            result = ssh_command("velocity")
            reply["text"] = f"<b>SpeedTest:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        elif text == "🔄 Reiniciar Servicios":
            reply["text"] = "🔄 Reiniciando servicios..."
            result = ssh_command("reiniciarservicos")
            reply["text"] = "✅ Servicios reiniciados."

        # Enviar respuesta a Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        import requests
        requests.post(url, json=reply)

        return 'ok', 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return 'error', 500

# === RUTA DE PRUEBA ===
@app.route('/')
def home():
    return "Bot de Telegram funcionando en Render 🚀", 200
