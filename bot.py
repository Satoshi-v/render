# bot.py - Bot idéntico al original, pero con webhook y usando tu sistema real
from flask import Flask, request
import logging
import paramiko
import requests
import json
import random
import string
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN (en Render como variables de entorno) ===
TOKEN = "7985103761:AAEcCdKMmchwm8rkXyLP0eQ5VvLJDNpfLBE"  # ← Cambia en Render
VPS_IP = "149.50.150.163"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA_DEL_VPS"  # ← Cambia esto

# === Diccionario temporal para controlar pruebas (como user_data en el original) ===
user_data = {}

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
        return f"❌ Error SSH: {str(e)}"

# === ENVIAR MENSAJE A TELEGRAM ===
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

# === MENÚ PRINCIPAL ===
def get_start_menu():
    return json.dumps({
        "inline_keyboard": [
            [{"text": "GERAR TESTE SSH 🤖", "callback_data": "generate_ssh_test"}],
            [{"text": "BOT DO WHATS", "url": "http://wa.me/+5575991044171"}],
            [{"text": "SUPORTE ⚙️", "url": "https://t.me/ntsoff1kytbr"}]
        ]
    })

# === RUTA PRINCIPAL ===
@app.route('/')
def home():
    return "Bot funcionando 🚀", 200

# === WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"📩 Recibido: {data}")

        # Manejar /start
        if 'message' in data and data['message']['text'] == '/start':
            user_name = data['message']['from']['first_name']
            chat_id = data['message']['chat']['id']

            start_message = (
                f"Olá {user_name}, Seja bem-vindo!\n"
                "APP PARA USAR O TESTE SSH📡 -> /apk\n"
                "<a href='https://t.me/ntsreferencias'>REFERÊNCIAS📌</a>\n"
                "<a href='https://ntsoff1.000webhostapp.com'>COMPRAR ACESSO VIP👤</a>"
            )

            enviar(
                chat_id,
                start_message,
                reply_markup=get_start_menu(),
                parse_mode="HTML"
            )

        # Manejar callback de botones
        elif 'callback_query' in data:
            query = data['callback_query']
            user_id = query['from']['id']
            chat_id = query['message']['chat']['id']
            data_callback = query['data']

            if data_callback == "generate_ssh_test":
                # Verificar si ya solicitó un test en los últimos 7 días
                if user_id in user_data and time.time() - user_data[user_id]['timestamp'] < 7 * 24 * 60 * 60:
                    error_msg = (
                        "⚠️ OPA VOCÊ JÁ SOLICITOU UM TESTE\n"
                        "AGUARDE 7 DIAS E PEÇA UM NOVO TESTE\n"
                        "COMPRAR ACESSO VIP @ntsoff1kytbr"
                    )
                    enviar(chat_id, error_msg)
                    # Borrar mensaje después de 10 segundos
                    time.sleep(10)
                    # Aquí no podemos borrar el mensaje sin bot, pero puedes usar un job si usas polling
                else:
                    # Generar test usando tu sistema real
                    enviar(chat_id, "⏳ Ejecutando... (esto puede tardar unos segundos)")
                    resultado = ssh_command("/bin/criarteste")

                    # Extraer usuario y contraseña del resultado (ajusta según tu salida)
                    # Suponiendo que la salida es como:
                    # USUÁRIO: testeabc123
                    # SENHA: 123456
                    lines = resultado.split('\n')
                    username = "não encontrado"
                    password = "não encontrado"
                    for line in lines:
                        if "USUÁRIO:" in line:
                            username = line.split("USUÁRIO:")[-1].strip()
                        if "SENHA:" in line:
                            password = line.split("SENHA:")[-1].strip()

                    ssh_test_info = (
                        f"⚠️ TESTE GERADO COM SUCESSO! ⚠️\n"
                        f"👤 USUÁRIO: <code>{username}</code>\n"
                        f"🔒 SENHA: <code>{password}</code>\n"
                        f"⏳ EXPIRA EM: 1 DIA\n"
                        f"️📂 BAIXAR APP  /apk"
                    )
                    enviar(chat_id, ssh_test_info, parse_mode="HTML")

                    # Guardar timestamp
                    user_data[user_id] = {
                        'username': username,
                        'password': password,
                        'timestamp': time.time()
                    }

            elif data_callback == "menu":
                enviar(chat_id, "Escolha uma opção:", reply_markup=get_start_menu())

        # Manejar comandos como /apk, /fogo_vpn, /doa
        elif 'message' in data and 'text' in data['message']:
            text = data['message']['text']
            chat_id = data['message']['chat']['id']

            if text == "/apk":
                enviar_apk(chat_id)
            elif text == "/fogo_vpn":
                enviar_apk2(chat_id)
            elif text.startswith("/doa"):
                doa(chat_id, text)

        return 'ok', 200

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 'error', 500

# === COMANDOS ===
def enviar_apk(chat_id):
    enviar(chat_id, "Enviando arquivo 📁. Por favor, aguarde... 📌", parse_mode='HTML')
    time.sleep(2)
    url = 'https://nts4g.000webhostapp.com/CAIXA_VIP.apk'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Telegram no permite enviar archivos directamente desde URL, necesitas subirlo
            # Pero como es webhook, no podemos usar bot.send_document fácilmente
            # Solución: enviar enlace de descarga
            enviar(chat_id, f"📥 Descarga el APK: {url}")
        else:
            enviar(chat_id, "❌ Ocorreu um erro ao baixar o arquivo.")
    except Exception as e:
        enviar(chat_id, f"❌ Erro: {str(e)}")

def enviar_apk2(chat_id):
    enviar(chat_id, "Enviando arquivo 📁. Por favor, aguarde... 📌", parse_mode='HTML')
    time.sleep(2)
    url = 'https://nts4g.000webhostapp.com/FOGO_VPN.apk'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            enviar(chat_id, f"📥 Descarga FOGO_VPN: {url}")
        else:
            enviar(chat_id, "❌ Ocorreu um erro ao baixar o arquivo.")
    except Exception as e:
        enviar(chat_id, f"❌ Erro: {str(e)}")

def doa(chat_id, text):
    valor = text.replace("/doa", "").strip()
    mensagem = (
        "CHAVE PIX 🔑 EMAIL ABAIXO\n"
        "PARA DOAÇÕES 😀\n"
        f"ntsoff1k@gmail.com: {valor}"
    )
    enviar(chat_id, mensagem)

# === FIN DEL CÓDIGO ===
