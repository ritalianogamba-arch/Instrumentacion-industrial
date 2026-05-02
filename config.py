import logging

# =========================================================================
# ZONA 0: CONFIGURACION
# =========================================================================

# PLC Connection Settings
PLC_IP = '192.168.1.10'
PLC_PORT = 502
MODBUS_TIMEOUT = 5
MODBUS_RETRIES = 2

# Flask Settings
FLASK_PORT = 8080
FLASK_HOST = '0.0.0.0'
DEBUG_MODE = False

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
