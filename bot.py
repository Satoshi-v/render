# bot.py - Bot compatible con webhook y Render
from flask import Flask, request
import logging
import paramiko
import requests
import json
import random
import string
import time
import sqlite3
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN (en Render como variables de entorno) ===
TOKEN = "TU_TOKEN_DE_TELEGRAM"
VPS_IP = "TU_IP_DEL_VPS"
VPS_USER = "root"
VPS_PASS = "TU_CONTRASENIA_DEL_VPS"

# === BASE DE DATOS DE USUARIOS ===
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        last_test_timestamp REAL
    )
''')
conn.commit()

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

# === MENÚ PRINCIPAL ===
def get_start_menu():
    return json.dumps({
        "inline_keyboard": [
            [{"text": "GERAR TESTE SSH 🤖", "callback_data": "generate_ssh_test"}],
            [{"text": "BOT DO WHATS", "url": "http://wa.me/+5575991044171"}],
            [{"text": "SUPORTE ⚙️", "url": "https://t.me/ntsoff1kytbr"}]
        ]
    })

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
                cursor.execute("SELECT last_test_timestamp FROM users WHERE user_id=?", (user_id,))
                result = cursor.fetchone()
                if result and time.time() - result[0] < 7 * 24 * 60 * 60:
                    error_msg = (
                        "⚠️ OPA VOCÊ JÁ SOLICITOU UM TESTE\n"
                        "AGUARDE 7 DIAS E PEÇA UM NOVO TESTE\n"
                        "COMPRAR ACESSO VIP @ntsoff1kytbr"
                    )
                    enviar(chat_id, error_msg)
                    # Borrar mensaje después de 10 segundos
                    time.sleep(10)
                else:
                    # Generar test usando comandos manuales
                    enviar(chat_id, "⏳ Ejecutando... (esto puede tardar unos segundos)")
                    random_username = f"teste{''.join(random.choices(string.ascii_lowercase, k=5))}"
                    random_password = ''.join(random.choices(string.digits, k=6))
                    create_user_command = f"sudo useradd -m -e $(date -d '+1 day') {random_username} -p $(openssl passwd -1 {random_password})"
                    ssh_command(create_user_command)

                    ssh_test_info = (
                        f"⚠️ TESTE GERADO COM SUCESSO! ⚠️\n"
                        f"👤 USUÁRIO: <code>{random_username}</code>\n"
                        f"🔒 SENHA: <code><pre>{random_password}</pre></code>\n"
                        f"⏳ EXPIRA EM: 1 DIA\n"
                        f"️📂 BAIXAR APP  /apk"
                    )
                    enviar(chat_id, ssh_test_info, parse_mode="HTML")

                    # Guardar timestamp
                    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (user_id, time.time()))
                    conn.commit()

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
    apk_url = 'https://nts4g.000webhostapp.com/CAIXA_VIP.apk'
    try:
        response = requests.get(apk_url)
        if response.status_code == 200:
            local_file_path = '/tmp/CAIXA_VIP.apk'
            with open(local_file_path, 'wb') as apk_file:
                apk_file.write(response.content)
            with open(local_file_path, 'rb') as apk_file:
                update.message.reply_document(document=apk_file, filename='CAIXA_VIP.apk')
            os.remove(local_file_path)
        else:
            enviar(chat_id, "❌ Ocorreu um erro ao baixar o arquivo.")
    except Exception as e:
        enviar(chat_id, f"❌ Erro: {str(e)}")

def enviar_apk2(chat_id):
    enviar(chat_id, "Enviando arquivo 📁. Por favor, aguarde... 📌", parse_mode='HTML')
    time.sleep(2)
    apk_url = 'https://nts4g.000webhostapp.com/FOGO_VPN.apk'
    try:
        response = requests.get(apk_url)
        if response.status_code == 200:
            local_file_path = '/tmp/FOGO_VPN.apk'
            with open(local_file_path, 'wb') as apk_file:
                apk_file.write(response.content)
            mensagem_personalizada = "⚙️ 𝑂 𝐴𝑃𝑃 𝑁𝐴̃𝑂 𝑃𝑅𝐸𝐶𝐼𝑆𝐴 𝐶𝑂𝐿𝑂𝐶𝐴𝑅 𝑁𝐸𝑀 🔐𝑆𝐸𝑁𝐻𝐴 𝐸 𝑁𝐸𝑀 👤𝑈𝑆𝑈𝐴́𝑅𝐼𝑂\n🗃️ 𝐸𝑁𝐕𝐼𝐴𝑁𝐷𝑂 𝐴𝐺𝑈𝐴𝑅𝐷𝐸 𝑂 𝐴𝑃𝑃"
            mensagem_enviada = update.message.reply_text(mensagem_personalizada)
            def remover_mensagem_personalizada():
                mensagem_enviada.delete()
            timer_mensagem_personalizada = threading.Timer(20, remover_mensagem_personalizada)
            timer_mensagem_personalizada.start()
            with open(local_file_path, 'rb') as apk_file:
                update.message.reply_document(document=apk_file, filename='FOGO_VPN.apk')
            os.remove(local_file_path)
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
