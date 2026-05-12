import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, logger

def obtener_url_ngrok():
    """
    Intenta obtener la URL pública de ngrok consultando la API local.
    """
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        response.raise_for_status()
        data = response.json()
        
        # Intentamos obtener la URL del primer túnel activo
        if data.get('tunnels'):
            return data['tunnels'][0]['public_url']
        return None
    except requests.exceptions.RequestException as e:
        logger.debug(f"No se pudo conectar a la API de ngrok: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Error al procesar la respuesta de ngrok: {e}")
        return None

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuario {update.effective_user.name} inició el bot")
    await update.message.reply_text(
        "🤖 Bot Servidor PLC\n\nComandos:\n/link - Obtener URL\n/status - Ver estado"
    )

async def comando_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = obtener_url_ngrok()
    if url:
        await update.message.reply_text(f"🌐 URL de la Interfaz PLC:\n{url}")
    else:
        await update.message.reply_text("❌ El servidor no tiene una URL pública activa (ngrok)")

async def comando_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = obtener_url_ngrok()
    if url:
        await update.message.reply_text(f"✅ Servidor ACCESIBLE\n\n🌐 URL:\n{url}")
    else:
        await update.message.reply_text("❌ Servidor OFFLINE o ngrok cerrado")

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN no configurado en config/telegram_cfg.py")
        return

    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", comando_start))
        application.add_handler(CommandHandler("link", comando_link))
        application.add_handler(CommandHandler("status", comando_status))
        
        logger.info("🤖 Bot Telegram iniciado y escuchando...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error crítico en el bot de Telegram: {e}")

if __name__ == '__main__':
    main()