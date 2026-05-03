import time
import threading
from pymodbus.client import ModbusTcpClient
from config import PLC_IP, PLC_PORT, MODBUS_TIMEOUT, MODBUS_RETRIES, logger

# =========================================================================
# ZONA 1: CLIENTE MODBUS CON THREAD SAFETY
# =========================================================================
client_lock = threading.Lock()

class ModbusClientManager:
    def __init__(self, ip, port, timeout=MODBUS_TIMEOUT):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.client = None
        self.next_reconnect_allowed = 0 # Timestamp para cooldown
        self.is_disabled = False # Estado para pruebas cuando no hay PLC
        self._connect()
    
    def _connect(self):
        try:
            self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
            self.client.connect()
            if self.client.is_socket_open():
                logger.info(f"Conexión Modbus establecida: {self.ip}:{self.port}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error en conexión inicial: {e}")
            return False
    
    def is_connected(self):
        return self.client and self.client.is_socket_open()
    
    def reconnect(self):
        if self.is_disabled:
            return False

        now = time.time()
        if now < self.next_reconnect_allowed:
            return False 

        for attempt in range(1, MODBUS_RETRIES + 1):
            try:
                if self.client:
                    self.client.close()
                
                logger.info(f"Intento de reconexión {attempt}/{MODBUS_RETRIES}...")
                time.sleep(0.5) 
                
                if self._connect():
                    self.next_reconnect_allowed = 0
                    self.is_disabled = False
                    return True
            except Exception as e:
                logger.error(f"Fallo en intento {attempt}: {e}")
        
        logger.error(f"No se pudo restablecer la conexión tras {MODBUS_RETRIES} intentos.")
        logger.error("SISTEMA EN MODO DESHABILITADO (SIMULACIÓN).")
        self.is_disabled = True # Deshabilitar intentos automáticos constantes
        self.next_reconnect_allowed = time.time() + 300 # Cooldown largo (5 min) si alguien intenta forzar
        return False

client_manager = ModbusClientManager(PLC_IP, PLC_PORT)

# =========================================================================
# ZONA 2: FUNCION DE ROBUSTEZ (CONEXION SEGURA CON THREAD SAFETY)
# =========================================================================
def safe_modbus_operation(operation_func, **kwargs):
    """
    Ejecuta operación Modbus de forma segura con auto-reconexión.
    Thread-safe gracias al lock.
    """
    with client_lock:
        if client_manager.is_disabled:
            return None

        try:
            if not client_manager.is_connected():
                logger.warning("Reconectando a Modbus...")
                if not client_manager.reconnect():
                    return None
            
            result = operation_func(client_manager.client, **kwargs)
            
            if result and result.isError():
                logger.warning(f"Error en operación Modbus: {result}")
                return None
            
            return result
        
        except Exception as e:
            logger.error(f"Excepción en operación: {e}")
            return None

# Wrappers para las operaciones comunes
def read_coils_safe(address, count=1):
    return safe_modbus_operation(lambda c, **kw: c.read_coils(**kw), address=address, count=count)

def write_coil_safe(address, value):
    return safe_modbus_operation(lambda c, **kw: c.write_coil(**kw), address=address, value=value)

def read_registers_safe(address, count=1):
    return safe_modbus_operation(lambda c, **kw: c.read_holding_registers(**kw), address=address, count=count)

def write_register_safe(address, value):
    return safe_modbus_operation(lambda c, **kw: c.write_register(**kw), address=address, value=value)
