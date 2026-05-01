import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = '8439612567:AAGX6hBDJov2PuyeljEMULHSATNvsCYpLoM'

def obtener_url_ngrok():
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        return response.json()['tunnels'][0]['public_url']
    except:
        return None

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Servidor PLC\n\nComandos:\n/link - Obtener URL\n/status - Ver estado"
    )

async def comando_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = obtener_url_ngrok()
    if url:
        await update.message.reply_text(f"🌐 URL de la Interfaz PLC:\n{url}")
    else:
        await update.message.reply_text("❌ El servidor está apagado")

async def comando_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = obtener_url_ngrok()
    if url:
        await update.message.reply_text(f"✅ Servidor ENCENDIDO\n\n🌐 URL:\n{url}")
    else:
        await update.message.reply_text("❌ Servidor APAGADO")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CommandHandler("link", comando_link))
    application.add_handler(CommandHandler("status", comando_status))
    
    print("🤖 Bot Telegram iniciado")
    application.run_polling()

if __name__ == '__main__':
    main()