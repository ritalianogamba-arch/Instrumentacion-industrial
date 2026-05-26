import requests
import logging
import os
import base64
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import Conflict
from config.telegram_cfg import TELEGRAM_TOKEN
from config.data import LISTA_TANQUES, LISTA_VALVULAS, LISTA_ACTUADORES
from config.logging_cfg import logger
from modbus_core import get_sensor_value, client_manager, read_coils_safe
from config.plc import raw_to_celsius, raw_to_level_percent
import time


def _load_dotenv(filepath='.env'):
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        logging.warning(f'No se pudo leer el archivo de entorno: {filepath}')


_load_dotenv()

def get_coil_value(address):
    res = read_coils_safe(address, count=1)
    return res.bits[0] if res else False

def obtener_url_ngrok():
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        response.raise_for_status()
        data = response.json()
        if data.get('tunnels'):
            return data['tunnels'][0]['public_url']
        return None
    except Exception:
        return None


def update_enlace_json(owner, repo, path, ngrok_url, branch='main', commit_msg="Update enlace.json from bot"):
    """Actualiza (o crea) el archivo `path` en el repo especificado usando la GitHub API.
    Requiere las variables de entorno `GITHUB_TOKEN` (token con permiso `repo`).
    Devuelve True si la operación tuvo éxito.
    """
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        logging.warning('GITHUB_TOKEN no configurado; no se puede actualizar el repo.')
        return False

    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # Ensure target branch exists; if not and branch != 'main', try to create it from 'main'
    if branch != 'main':
        ref_api = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
        try:
            rref = requests.get(ref_api, headers=headers, timeout=5)
            if rref.status_code == 404:
                # create branch from main
                main_ref_api = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/main"
                rmain = requests.get(main_ref_api, headers=headers, timeout=5)
                if rmain.status_code == 200:
                    main_sha = rmain.json().get('object', {}).get('sha')
                    if main_sha:
                        create_ref_api = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
                        payload_ref = {"ref": f"refs/heads/{branch}", "sha": main_sha}
                        rcreate = requests.post(create_ref_api, headers=headers, json=payload_ref, timeout=10)
                        if rcreate.status_code not in (201, 200):
                            logging.error(f'No se pudo crear la rama {branch} en el repo: {rcreate.status_code} {rcreate.text}')
                            return False
                    else:
                        logging.error('No se pudo obtener SHA de main para crear nueva rama')
                        return False
                else:
                    logging.error('No existe la rama main para basar la nueva rama')
                    return False
        except Exception as e:
            logging.error(f'Error verificando/creando rama en GitHub: {e}')
            return False
    content = json.dumps({"url_ngrok": ngrok_url}, ensure_ascii=False).encode('utf-8')
    b64 = base64.b64encode(content).decode('utf-8')
    try:
        # Try to fetch existing file in the target branch
        r = requests.get(api, headers=headers, params={'ref': branch}, timeout=5)
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
        # include branch in payload so commit goes to the right branch
        payload['branch'] = branch
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
    modo_actual = "REAL (PLC) 🟢" if client_manager.is_connected() else "DESCONECTADO 🔴"
    
    reporte = "🏭 *REPORTE DE PLANTA SCADA*\n"
    reporte += f"📡 Modo de Operación: *{modo_actual}*\n"
    reporte += "=========================\n\n"
    
    for t in LISTA_TANQUES:
        reporte += f"🛢️ *{t.nombre}*:\n"
        tiene_datos = False
        
        if t.sensor_de_presion:
            raw_nivel = get_sensor_value(t.sensor_de_presion)
            nivel = raw_to_level_percent(raw_nivel, t.min_val, t.max_val)
            reporte += f"  💧 Nivel: `{nivel:.1f} %`\n"
            tiene_datos = True
            
        if t.sensor_de_temperatura:
            raw_temp = get_sensor_value(t.sensor_de_temperatura)
            temp = raw_to_celsius(raw_temp)
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
            owner = os.environ.get('GITHUB_OWNER', '').strip()
            repo = os.environ.get('GITHUB_REPO', '').strip()
            target_branch = os.environ.get('GITHUB_TARGET_BRANCH', 'main').strip()
            if owner and repo:
                saved = update_enlace_json(owner, repo, 'docs/enlace.json', url, branch=target_branch)
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