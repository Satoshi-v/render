# bot.py - Versión con depuración avanzada
from flask import Flask, request
import logging
import paramiko
import requests

# === CONFIGURACIÓN ===
TOKEN = "TU_TOKEN_DE_TELEGRAM"
VPS_IP = "TU_IP_DEL_VPS"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA"

app = Flask(__name__)

# Configurar logging para ver todo en los logs de Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FUNCIÓN SSH MEJORADA ===
def ssh_command(cmd):
    try:
        logger.info(f"Ejecutando comando SSH: {cmd}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=10)
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        client.close()

        if error:
            logger.error(f"Error en SSH: {error}")
            return f"❌ Error: {error.strip()}"
        if output:
            logger.info(f"Salida SSH: {output.strip()}")
            return output.strip()
        return "✅ Comando ejecutado (sin salida)."
    except Exception as e:
        logger.error(f"Excepción en SSH: {str(e)}")
        return f"❌ Error SSH: {str(e)}"

# === MENÚ ===
keyboard = {
    "keyboard": [
        [{"text": "🔐 Generar Test"}],
        [{"text": "📊 Usuarios Online"}, {"text": "⚡ SpeedTest"}]
    ],
    "resize_keyboard": True
}

# === RUTA WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"🔹 Datos recibidos de Telegram: {data}")  # ← Aquí ves si llega algo

        if not data:
            logger.warning("No se recibieron datos")
            return 'No data', 400

        # Verificar si es un mensaje
        if 'message' not in data:
            logger.warning("No es un mensaje válido")
            return 'Not a message', 200

        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        logger.info(f"📩 Mensaje recibido de {chat_id}: {text}")  # ← Aquí ves si /start llega

        # Enviar respuesta
        def send_telegram(texto, markup=None):
            reply = {
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML"
            }
            if markup:
                reply["reply_markup"] = markup

            logger.info(f"📤 Enviando a Telegram: {reply}")
            try:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=reply, timeout=10)
            except Exception as e:
                logger.error(f"❌ Error al enviar a Telegram: {e}")

        # Procesar comandos
        if text == "/start":
            logger.info("✅ Comando /start detectado")
            send_telegram("👋 ¡Hola! Usa el menú:", keyboard)

        elif text == "🔐 Generar Test":
            send_telegram("⏳ Generando test...")
            result = ssh_command("/bin/criarteste")
            send_telegram(f"<b>Resultado:</b>\n<pre>{result}</pre>")

        elif text == "📊 Usuarios Online":
            send_telegram("🔍 Cargando...")
            result = ssh_command("/bin/sshmonitor")
            send_telegram(f"<b>Usuarios:</b>\n<pre>{result}</pre>")

        elif text == "⚡ SpeedTest":
            send_telegram("📡 Speedtest...")
            result = ssh_command("/bin/velocity")
            send_telegram(f"<b>SpeedTest:</b>\n<pre>{result}</pre>")

        else:
            send_telegram("🤖 Usa el menú:", keyboard)

        return 'ok', 200

    except Exception as e:
        logger.error(f"❌ Error en webhook: {str(e)}")
        return 'error', 500

# === RUTA DE PRUEBA ===
@app.route('/')
def home():
    logger.info("🏠 Ruta / accedida")
    return "Bot funcionando 🚀", 200
