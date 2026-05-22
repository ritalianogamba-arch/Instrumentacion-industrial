import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import Conflict
from config import TELEGRAM_TOKEN, LISTA_TANQUES, LISTA_VALVULAS, LISTA_ACTUADORES, logger
from modbus_core import get_sensor_value, client_manager, read_coils_safe
import time

def get_coil_value(address):
    if client_manager.is_disabled:
        import mocks
        return mocks.mock_read_coil(address)
    res = read_coils_safe(address, count=1)
    return res.bits[0] if res else False

def obtener_url_ngrok():
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        response.raise_for_status()
        data = response.json()
        if data.get('tunnels'):
            return data['tunnels'][0]['public_url']
        return None
    except Exception:
        return None

def generar_reporte_telemetria():
    """Genera un reporte formateado leyendo directamente los sensores."""
    # Determinar si estamos usando datos físicos o el simulador
    modo_actual = "SIMULADO 🟡" if (not client_manager.is_connected() or client_manager.is_disabled) else "REAL (PLC) 🟢"
    
    reporte = "🏭 *REPORTE DE PLANTA SCADA*\n"
    reporte += f"📡 Modo de Operación: *{modo_actual}*\n"
    reporte += "=========================\n\n"
    
    for t in LISTA_TANQUES:
        reporte += f"🛢️ *{t.nombre}*:\n"
        tiene_datos = False
        
        if t.sensor_de_presion:
            nivel = get_sensor_value(t.sensor_de_presion)
            reporte += f"  💧 Nivel: `{nivel:.1f} %`\n"
            tiene_datos = True
            
        if t.sensor_de_temperatura:
            temp = get_sensor_value(t.sensor_de_temperatura)
            reporte += f"  🌡️ Temp: `{temp:.1f} °C`\n"
            tiene_datos = True
            
        if not tiene_datos:
            reporte += "  (Sin sensores analógicos)\n"
        reporte += "\n"

    # ACTUADORES ANALÓGICOS
    reporte += "⚙️ *ACTUADORES ANALÓGICOS*:\n"
    for a in LISTA_ACTUADORES:
        if "Resistencia" not in a.nombre:
            raw_val = get_sensor_value(a.address)
            scale = 50.0 if a.unidad == 'Hz' else 100.0
            divisor = (a.max_val - a.min_val) / scale
            val = max(0.0, min(scale, (raw_val - a.min_val) / divisor))
            reporte += f"  🔸 {a.nombre}: `{val:.1f} {a.unidad}`\n"
    reporte += "\n"

    # VÁLVULAS (SALIDAS DIGITALES)
    reporte += "🚰 *VÁLVULAS (ESTADO REAL)*:\n"
    for v in LISTA_VALVULAS:
        estado = get_coil_value(v.address)
        icono = "🟢 ABIERTA" if estado else "🔴 CERRADA"
        reporte += f"  🔹 {v.nombre}: {icono}\n"
        
    return reporte

def get_main_menu():
    """Retorna los botones del menú interactivo."""
    keyboard = [
        [InlineKeyboardButton("📊 Ver Telemetría", callback_data='menu_telemetria')],
        [InlineKeyboardButton("🔗 Obtener Link de Acceso", callback_data='menu_link')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuario {update.effective_user.name} inició el bot")
    await update.message.reply_text(
        "🤖 *Panel de Control SCADA*\n\n¡Hola! Soy tu asistente de planta.\nSelecciona una acción:",
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Acknowledge el click
    
    if query.data == 'menu_telemetria':
        reporte = generar_reporte_telemetria()
        await query.edit_message_text(text=reporte, parse_mode='Markdown', reply_markup=get_main_menu())
        
    elif query.data == 'menu_link':
        url = obtener_url_ngrok()
        if url:
            mensaje = f"🌐 *Enlace Seguro a SCADA:*\n{url}"
        else:
            mensaje = "❌ *El servidor web externo (ngrok) está offline.*"
        await query.edit_message_text(text=mensaje, parse_mode='Markdown', reply_markup=get_main_menu())

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN no configurado en config/telegram_cfg.py")
        return

    while True:
        try:
            # Se agrega drop_pending_updates para limpiar cola antigua y evitar conflictos rápidos
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            application.add_handler(CommandHandler("start", comando_start))
            application.add_handler(CallbackQueryHandler(manejar_botones))
            
            logger.info("🤖 Bot Telegram iniciando con Menú Interactivo...")
            
            # Ejecución con control de excepciones para modo Reload de Flask
            application.run_polling(drop_pending_updates=True, stop_signals=())
            
            # Si sale de run_polling sin errores, rompemos el ciclo
            break
            
        except Conflict:
            logger.warning("Bot Telegram: Conflicto detectado (Doble Instancia). Reintentando en 3 segundos...")
            time.sleep(3)
        except Exception as e:
            logger.error(f"Error crítico en el bot de Telegram: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()