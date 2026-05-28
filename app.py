import threading
import os
from flask import Flask
from config import FLASK_HOST, FLASK_PORT, DEBUG_MODE, logger
from modbus_core import client_manager
from api_routes import api_bp
from bot_telegram import main as run_bot

app = Flask(__name__)

# Registrar las rutas
app.register_blueprint(api_bp)

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO SISTEMA SCADA")
    logger.info("=" * 60)
    
    # Solo iniciar hilos si es el proceso principal (para evitar duplicados con el reloader)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not DEBUG_MODE:
        logger.info("📦 Iniciando servicios en segundo plano...")
        
        # Bot de Telegram
        threading.Thread(target=run_bot, daemon=True, name="BotTelegram").start()
        logger.info("✅ Bot Telegram activo")
        
        # Calculador de Caudal PID LAB
        from caudal_calculator import run_caudal_calculator
        threading.Thread(target=run_caudal_calculator, daemon=True, name="CaudalCalc").start()
        logger.info("✅ Calculador de Caudal activo")

    try:
        # Iniciar servidor Flask
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
    finally:
        if client_manager.client:
            client_manager.client.close()
        logger.info("Conexión Modbus cerrada")