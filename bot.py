# bot.py - Primer paso: Conexión SSH desde el bot
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import paramiko

# === CONFIGURACIÓN desde variables de entorno (seguro) ===
TOKEN = os.getenv("TOKEN")           # Tu token de Telegram
VPS_IP = os.getenv("VPS_IP")         # Ej: 149.50.150.163
VPS_USER = os.getenv("VPS_USER")     # Ej: root
VPS_PASS = os.getenv("VPS_PASS")     # Tu contraseña del VPS

# === COMANDO /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de gestión.\n"
        "Escribe /ssh para probar la conexión con tu VPS."
    )

# === COMANDO /ssh - Probar conexión SSH ===
async def ssh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Conectando a tu VPS por SSH...")

    try:
        # Crear cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conectarse al VPS
        ssh_client.connect(
            hostname=VPS_IP,
            username=VPS_USER,
            password=VPS_PASS,
            timeout=10
        )

        # Ejecutar un comando simple
        stdin, stdout, stderr = ssh_client.exec_command("whoami")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        ssh_client.close()

        if error:
            await update.message.reply_text(f"❌ Error en el VPS:\n<pre>{error}</pre>", parse_mode="HTML")
        else:
            await update.message.reply_text(f"✅ Conexión exitosa!\nEl usuario en el VPS es: <b>{output}</b>", parse_mode="HTML")

    except Exception as e:
        await update.message.reply_text(f"🔴 Fallo al conectar por SSH:\n<pre>{str(e)}</pre>", parse_mode="HTML")

# === INICIAR EL BOT ===
def main():
    if not all([TOKEN, VPS_IP, VPS_USER, VPS_PASS]):
        print("❌ Error: Faltan variables de entorno (TOKEN, VPS_IP, VPS_USER, VPS_PASS)")
        return

    print("Bot iniciado. Conectando a Telegram...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ssh", ssh))

    app.run_polling()

if __name__ == "__main__":
    main()
