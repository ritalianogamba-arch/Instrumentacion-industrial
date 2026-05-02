import threading
from flask import Flask
from config import FLASK_HOST, FLASK_PORT, DEBUG_MODE, logger
from modbus_core import client_manager
from api_routes import api_bp
from supervisors import supervisor_tacho_2, supervisor_tacho_4

app = Flask(__name__)

# Registrar las rutas desde el Blueprint
app.register_blueprint(api_bp)

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Iniciando Servidor SCADA Tank Control (Modular)")
    logger.info("=" * 60)
    
    # Iniciar supervisores en hilos separados
    t2_thread = threading.Thread(target=supervisor_tacho_2, daemon=True, name="Supervisor-T2")
    t4_thread = threading.Thread(target=supervisor_tacho_4, daemon=True, name="Supervisor-T4")
    
    t2_thread.start()
    t4_thread.start()
    
    logger.info(f"Servidores SCADA corriendo en {FLASK_HOST}:{FLASK_PORT}")
    
    try:
        # Intentar SSL primero
        try:
            app.run(
                host=FLASK_HOST, 
                port=FLASK_PORT, 
                ssl_context=('server.crt', 'server.key'), 
                debug=DEBUG_MODE,
                use_reloader=False
            )
        except FileNotFoundError:
            logger.warning("Certificados SSL no encontrados, ejecutando en HTTP")
            app.run(
                host=FLASK_HOST, 
                port=FLASK_PORT, 
                debug=DEBUG_MODE,
                use_reloader=False
            )
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
    finally:
        if client_manager.client:
            client_manager.client.close()
        logger.info("Conexión Modbus cerrada")