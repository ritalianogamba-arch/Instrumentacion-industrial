import requests
import logging
import os
import base64
import json
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


def update_enlace_json(owner, repo, path, ngrok_url, commit_msg="Update enlace.json from bot"):
    """Actualiza (o crea) el archivo `path` en el repo especificado usando la GitHub API.
    Requiere las variables de entorno `GITHUB_TOKEN` (token con permiso `repo`).
    Devuelve True si la operación tuvo éxito.
    """
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        logging.warning('GITHUB_TOKEN no configurado; no se puede actualizar el repo.')
        return False

    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    content = json.dumps({"url_ngrok": ngrok_url}, ensure_ascii=False).encode('utf-8')
    b64 = base64.b64encode(content).decode('utf-8')
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    try:
        r = requests.get(api, headers=headers, timeout=5)
        sha = None
        if r.status_code == 200:
            sha = r.json().get('sha')
    except Exception as e:
        logging.error(f'Error consultando archivo en GitHub: {e}')
        sha = None

    payload = {"message": commit_msg, "content": b64}
    if sha:
        payload["sha"] = sha

    try:
        r = requests.put(api, headers=headers, json=payload, timeout=10)
        if r.status_code in (200, 201):
            logging.info('docs/enlace.json actualizado en GitHub')
            return True
        logging.error(f'GitHub update failed {r.status_code} {r.text}')
        return False
    except Exception as e:
        logging.error(f'Error actualizando archivo en GitHub: {e}')
        return False

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
            owner = os.environ.get('GITHUB_OWNER')
            repo = os.environ.get('GITHUB_REPO')
            if owner and repo:
                saved = update_enlace_json(owner, repo, 'docs/enlace.json', url)
                if saved:
                    mensaje += "\n\n🔁 Enlace guardado en repo (docs/enlace.json)."
                else:
                    mensaje += "\n\n⚠️ No se pudo guardar en repo (ver logs)."
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