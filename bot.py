# bot.py - Bot que usa TU sistema real
from flask import Flask, request
import logging
import paramiko
import json
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN (en Render como variables de entorno) ===
TOKEN = "7985103761:AAEcCdKMmchwm8rkXyLP0eQ5VvLJDNpfLBE"
VPS_IP = "149.50.150.163"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA_DEL_VPS"

# === EJECUTAR COMANDO EN VPS ===
def ssh_command(cmd):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=10)
        stdin, stdout, stderr = client.exec_command(f"bash -l -c '{cmd}'")
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        client.close()
        return f"{output}\n{error}".strip() if error else output
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === MENÚ CON UN SOLO BOTÓN ===
teclado = {
    "keyboard": [[{"text": "🔐 Generar Test"}]],
    "resize_keyboard": True
}

# === WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"📩 Recibido: {data}")

        if 'message' not in 
            return 'ok', 200

        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        if text == "/start":
            enviar(chat_id, "👋 Hola! Presiona el botón para generar un test.", teclado)

        elif text == "🔐 Generar Test":
            enviar(chat_id, "⏳ Generando test...")
            resultado = ssh_command("/bin/criarteste")
            enviar(chat_id, f"<b>Resultado:</b>\n<pre>{resultado}</pre>", parse_mode="HTML")

        return 'ok', 200

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'error', 500

# === ENVIAR A TELEGRAM ===
def enviar(chat_id, texto, reply_markup=None, parse_mode=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": parse_mode,
        "reply_markup": reply_markup
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        logger.info(f"📤 Enviado: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ No se pudo enviar: {e}")

@app.route('/')
def home():
    return "Bot funcionando 🚀", 200
