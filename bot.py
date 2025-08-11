# bot.py - Bot de Telegram con Webhook + SSH a tu VPS
from flask import Flask, request
import logging
import paramiko
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN (después las pondrás en Render como variables de entorno) ===
TOKEN = "7985103761:AAEcCdKMmchwm8rkXyLP0eQ5VvLJDNpfLBE"
VPS_IP = "149.50.150.163"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA_DEL_VPS"  # ← CAMBIA ESTO

# === FUNCIÓN PARA EJECUTAR COMANDOS EN EL VPS ===
def ejecutar_en_vps(comando):
    try:
        logger.info(f"Ejecutando en VPS: {comando}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=10)

        stdin, stdout, stderr = client.exec_command(comando)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        client.close()

        if error:
            logger.error(f"Error SSH: {error}")
            return f"❌ {error}"
        return output or "✅ Comando ejecutado."
    except Exception as e:
        logger.error(f"Fallo SSH: {str(e)}")
        return f"🔴 SSH falló: {str(e)}"

# === BOTONES (solo uno) ===
teclado_test = {
    "keyboard": [
        [{"text": "🔐 Generar Test"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

# === WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")

        # Verificar si hay un mensaje válido
        if 'message' not in data:
            logger.warning("No se encontró 'message' en los datos recibidos.")
            return 'ok', 200

        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        # Comando /start
        if text == "/start":
            logger.info(f"/start recibido de {chat_id}")
            enviar_mensaje(chat_id, "👋 Hola! Presiona el botón para generar un test.", teclado_test)

        # Botón: Generar Test
        elif text == "🔐 Generar Test":
            enviar_mensaje(chat_id, "⏳ Ejecutando... (esto puede tardar unos segundos)")
            resultado = ejecutar_en_vps("/bin/criarteste")
            enviar_mensaje(chat_id, f"<b>Resultado:</b>\n<pre>{resultado}</pre>", parse_mode="HTML")

        return 'ok', 200

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return 'error', 500

# === FUNCION PARA ENVIAR MENSAJES A TELEGRAM ===
def enviar_mensaje(chat_id, texto, reply_markup=None, parse_mode=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        logger.info(f"Enviado a Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"No se pudo enviar mensaje: {e}")

# === FIN DEL CÓDIGO ===
