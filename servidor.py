from flask import Flask, request, jsonify, render_template
from pymodbus.client import ModbusTcpClient
import time
import threading
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
        self._connect()
    
    def _connect(self):
        try:
            self.client = ModbusTcpClient(self.ip, port=self.port, timeout=self.timeout)
            self.client.connect()
            if self.client.is_socket_open():
                logger.info(f"✓ Conexión Modbus establecida: {self.ip}:{self.port}")
                return True
            return False
        except Exception as e:
            logger.error(f"✗ Error en conexión inicial: {e}")
            return False
    
    def is_connected(self):
        return self.client and self.client.is_socket_open()
    
    def reconnect(self):
        try:
            if self.client:
                self.client.close()
            time.sleep(0.1)
            return self._connect()
        except Exception as e:
            logger.error(f"✗ Fallo en reconexión: {e}")
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
        try:
            if not client_manager.is_connected():
                logger.warning("⚠ Reconectando a Modbus...")
                if not client_manager.reconnect():
                    logger.error("✗ No se pudo reconectar")
                    return None
            
            result = operation_func(client_manager.client, **kwargs)
            
            if result and result.isError():
                logger.warning(f"⚠ Error en operación Modbus: {result}")
                return None
            
            return result
        
        except Exception as e:
            logger.error(f"✗ Excepción en operación: {e}")
            client_manager.reconnect()
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

app = Flask(__name__)

# =========================================================================
# ZONA 3: RUTA PRINCIPAL (FRONTEND)
# =========================================================================
@app.route('/')
def index():
    return render_template('index.html', usuario="Operador", rol="supervisor")

# =========================================================================
# ZONA 4: API MODBUS BASICA (COILS Y REGISTERS)
# =========================================================================
@app.route('/read_coil', methods=['GET'])
def read_coil():
    try:
        address = int(request.args.get('address'))
        result = read_coils_safe(address, count=1)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo lectura'})
        return jsonify({'success': True, 'value': result.bits[0]})
    except Exception as e: 
        logger.error(f"Error en read_coil: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/write_coil', methods=['POST'])
def write_coil():
    try:
        data = request.get_json()
        address = data['address']
        value = bool(data['value'])
        result = write_coil_safe(address, value)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo escritura'})
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en write_coil: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/read_register', methods=['GET'])
def read_register():
    try:
        address = int(request.args.get('address'))
        result = read_registers_safe(address, count=1)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo lectura'})
        return jsonify({'success': True, 'value': result.registers[0]})
    except Exception as e: 
        logger.error(f"Error en read_register: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/write_register', methods=['POST'])
def write_register():
    try:
        data = request.get_json()
        address = data['address']
        value = int(data['value']) 
        # Proteccion: 300 y 400 son coils de seguridad
        if address == 300 or address == 400: 
             return jsonify({'success': False, 'error': 'Dirección reservada para supervisor.'})
        result = write_register_safe(address, value)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo escritura'})
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en write_register: {e}")
        return jsonify({'success': False, 'error': str(e)})

# =========================================================================
# ZONA 5: API DE ESTADO (MONITOREO GENERAL)
# =========================================================================
@app.route('/status')
def status():
    # 1. Lectura Coils
    coils_data = read_coils_safe(0, count=24)
    permiso_t4 = read_coils_safe(300, count=1)
    estado_t4  = read_coils_safe(350, count=1)
    permiso_t2 = read_coils_safe(400, count=1)
    estado_t2  = read_coils_safe(450, count=1)

    coils_in = coils_data.bits[:14] if coils_data else [False]*14
    coils_out = coils_data.bits[14:24] if coils_data else [False]*10

    pid_flags = {
        "t4_permiso": permiso_t4.bits[0] if permiso_t4 else False,
        "t4_activo":  estado_t4.bits[0] if estado_t4 else False,
        "t2_permiso": permiso_t2.bits[0] if permiso_t2 else False,
        "t2_activo":  estado_t2.bits[0] if estado_t2 else False
    }

    # 2. Analogicos
    ai = read_registers_safe(200, count=6)
    aq = read_registers_safe(301, count=4)
    reg_in = ai.registers if ai else [0]*6
    reg_out = aq.registers if aq else [0]*4
    
    # 3. SetPoints de Nivel
    sp_niv = read_registers_safe(101, count=5)
    sp_niveles = sp_niv.registers if sp_niv else [0]*5

    # 4. PIDs
    pid_t2_raw = read_registers_safe(400, count=8)
    pid_t2 = {}
    if pid_t2_raw:
        r = pid_t2_raw.registers
        pid_t2 = {
            'params': {'setpoint': round((r[0]*75/1000)+0.5, 1), 'kp': r[2]*0.01, 'ti': r[4]*0.1, 'td': r[6]*0.1},
            'status': {'temp_actual': round((r[1]*75/1000)+0.5, 1), 'error': round(r[3]*75/1000, 1), 'salida': r[5]/100.0}
        }

    pid_t4_raw = read_registers_safe(420, count=8)
    pid_t4 = {}
    if pid_t4_raw:
        r = pid_t4_raw.registers
        pid_t4 = {
            'params': {'setpoint': round((r[0]*75/1000)+0.5, 1), 'kp': r[2]*0.01, 'ti': r[4]*0.1, 'td': r[6]*0.1},
            'status': {'temp_actual': round((r[1]*75/1000)+0.5, 1), 'error': round(r[3]*75/1000, 1), 'salida': r[5]/100.0}
        }

    return jsonify({
        "coils_inputs": coils_in, "coils_outputs": coils_out, "pid_flags": pid_flags,
        "registers_inputs": reg_in, "registers_outputs": reg_out, "sp_niveles": sp_niveles,
        "pid_t2": pid_t2, "pid_t4": pid_t4
    })

# =========================================================================
# ZONA 6: API CONTROL PID
# =========================================================================
@app.route('/update_pid', methods=['POST'])
def update_pid():
    try:
        d = request.get_json()
        base = 400 if d.get('id') == 'T2' else 420
        sp_raw = int(((float(d['setpoint']) - 0.5) * 1000) / 75)
        kp_raw = int(float(d['kp']) / 0.01)
        ti_raw = int(float(d['ti']) / 0.1)
        td_raw = int(float(d['td']) / 0.1)
        
        write_register_safe(base, sp_raw)
        write_register_safe(base+2, kp_raw)
        write_register_safe(base+4, ti_raw)
        write_register_safe(base+6, td_raw)
        logger.info(f"✓ PID {d.get('id')} actualizado")
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en update_pid: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/reset_pid', methods=['POST'])
def reset_pid(): 
    logger.info("Reset PID solicitado")
    return jsonify({'success': True})

# =========================================================================
# ZONA 7: SUPERVISORES DE SEGURIDAD (SOLO NIVEL)
# =========================================================================

# --- SUPERVISOR TACHO 2 ---
def supervisor_tacho_2():
    logger.info("🔍 Supervisor T2 (%M400 Nivel) iniciado")
    ADDR_NIV = 204
    ADDR_PERM = 400
    MIN_RAW = 7000
    
    while True:
        try:
            r_n = read_registers_safe(ADDR_NIV, count=1)
            permiso = False
            
            if r_n:
                niv = r_n.registers[0]
                permiso = niv > MIN_RAW
                # logger.debug(f"[T2] Nivel: {niv} → Permiso: {permiso}")
            
            # Escritura forzada (Heartbeat)
            write_coil_safe(ADDR_PERM, permiso)
            time.sleep(1)
        except Exception as e:
            logger.error(f"⚠ Error en supervisor T2: {e}")
            time.sleep(5)

# --- SUPERVISOR TACHO 4 ---
def supervisor_tacho_4():
    logger.info("🔍 Supervisor T4 (%M300 Nivel) iniciado")
    ADDR_NIV = 203
    ADDR_PERM = 300
    MIN_RAW = 6300
    
    while True:
        try:
            r_n = read_registers_safe(ADDR_NIV, count=1)
            permiso = False
            
            if r_n:
                niv = r_n.registers[0]
                permiso = niv > MIN_RAW
                # logger.debug(f"[T4] Nivel: {niv} → Permiso: {permiso}")
            
            # Escritura forzada (Heartbeat)
            write_coil_safe(ADDR_PERM, permiso)
            time.sleep(1)
        except Exception as e:
            logger.error(f"⚠ Error en supervisor T4: {e}")
            time.sleep(5)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Iniciando Servidor SCADA Tank Control")
    logger.info("=" * 60)
    
    # Iniciar supervisores
    t2_thread = threading.Thread(target=supervisor_tacho_2, daemon=True, name="Supervisor-T2")
    t4_thread = threading.Thread(target=supervisor_tacho_4, daemon=True, name="Supervisor-T4")
    
    t2_thread.start()
    t4_thread.start()
    
    logger.info(f"✓ Servidores SCADA corriendo en {FLASK_HOST}:{FLASK_PORT}")
    
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
            logger.warning("⚠ Certificados SSL no encontrados, ejecutando en HTTP")
            app.run(
                host=FLASK_HOST, 
                port=FLASK_PORT, 
                debug=DEBUG_MODE,
                use_reloader=False
            )
    except KeyboardInterrupt:
        logger.info("⏹ Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"✗ Error fatal: {e}")
    finally:
        if client_manager.client:
            client_manager.client.close()
        logger.info("✓ Conexión Modbus cerrada")