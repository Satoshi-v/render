# bot.py - Bot de Telegram con Webhook + SSH a tu VPS
from flask import Flask, request
import logging
import paramiko
import json
import requests

# === CONFIGURACIÓN (usar variables de entorno en Render) ===
TOKEN = "TU_TOKEN_DE_TELEGRAM"  # ← Render: añade como variable
VPS_IP = "TU_IP_DEL_VPS"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA"

app = Flask(__name__)
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

# === MENÚ DE BOTONES (sin "Reiniciar Servicios") ===
keyboard = {
    "keyboard": [
        [{"text": "🔐 Generar Test"}],
        [{"text": "📊 Usuarios Online"}, {"text": "⚡ SpeedTest"}]
    ],
    "resize_keyboard": True
}

# === RUTA DEL WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")

        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        reply = {
            "chat_id": chat_id,
            "text": "🤖 Usa el menú:",
            "reply_markup": keyboard
        }

        if text == "/start":
            logger.info("Recibido comando /start")
            reply["text"] = "👋 ¡Hola! Usa el menú para gestionar tu VPS."

        elif text == "🔐 Generar Test":
            reply["text"] = "⏳ Generando usuario de prueba..."
            result = ssh_command("/bin/criarteste")  # ✅ Ejecuta directamente
            reply["text"] = f"<b>Usuario de prueba creado:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        elif text == "📊 Usuarios Online":
            reply["text"] = "🔍 Cargando usuarios online..."
            result = ssh_command("/bin/sshmonitor")
            reply["text"] = f"<b>Usuarios Online:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        elif text == "⚡ SpeedTest":
            reply["text"] = "📡 Ejecutando speedtest..."
            result = ssh_command("/bin/velocity")
            reply["text"] = f"<b>SpeedTest:</b>\n<pre>{result}</pre>"
            reply["parse_mode"] = "HTML"

        else:
            reply["text"] = "🤖 Usa el menú del bot."

        # Enviar respuesta a Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        try:
            response = requests.post(url, json=reply, timeout=10)
            logger.info(f"Respuesta de Telegram: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Error al enviar a Telegram: {e}")

        return 'ok', 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return 'error', 500

# === RUTA DE PRUEBA ===
@app.route('/')
def home():
    return "Bot de Telegram funcionando en Render 🚀", 200
