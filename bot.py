# bot.py - Bot de gestión mejorado y estable
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === CONFIGURACIÓN desde variables de entorno ===
TOKEN = os.getenv("TOKEN")
VPS_IP = os.getenv("VPS_IP")
VPS_USER = os.getenv("VPS_USER")
VPS_PASS = os.getenv("VPS_PASS")

# === CONFIGURACIÓN DE LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === COMANDO /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de gestión.\n"
        "Escribe /ssh para probar la conexión con tu VPS.",
        reply_markup=None
    )

# === COMANDO /ssh - Probar conexión SSH ===
async def ssh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Conectando a tu VPS por SSH...", reply_markup=None)

    try:
        import paramiko

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(
            hostname=VPS_IP,
            username=VPS_USER,
            password=VPS_PASS,
            timeout=10
        )

        stdin, stdout, stderr = ssh_client.exec_command("whoami")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh_client.close()

        if error:
            await update.message.reply_text(
                f"❌ Error en el VPS:\n<pre>{error}</pre>",
                parse_mode="HTML",
                reply_markup=None
            )
        else:
            await update.message.reply_text(
                f"✅ Conexión exitosa!\nEl usuario en el VPS es: <b>{output}</b>",
                parse_mode="HTML",
                reply_markup=None
            )

    except paramiko.AuthenticationException:
        await update.message.reply_text(
            "🔴 Fallo de autenticación. Verifica usuario o contraseña.",
            parse_mode="HTML",
            reply_markup=None
        )
    except paramiko.SSHException as e:
        await update.message.reply_text(
            f"🔴 Error SSH: <pre>{str(e)}</pre>",
            parse_mode="HTML",
            reply_markup=None
        )
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        await update.message.reply_text(
            f"🔴 Error al conectar: <pre>{type(e).__name__}: {str(e)}</pre>",
            parse_mode="HTML",
            reply_markup=None
        )

# === INICIAR EL BOT ===
def main():
    if not all([TOKEN, VPS_IP, VPS_USER, VPS_PASS]):
        logger.error("❌ Faltan variables de entorno: TOKEN, VPS_IP, VPS_USER, VPS_PASS")
        return

    logger.info("🚀 Bot iniciado. Conectando a Telegram...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ssh", ssh))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
