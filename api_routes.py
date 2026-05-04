from flask import Blueprint, request, jsonify, render_template
from config import logger, get_system_data, PLC_REMOTE_LOCK_ADDR
from modbus_core import (
    read_coils_safe, write_coil_safe, 
    read_registers_safe, write_register_safe,
    client_manager
)
from mocks import (
    get_mock_status, mock_read_coil, mock_write_coil, 
    mock_read_register, mock_write_register
)

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)

def check_remote_lock():
    """Verifica si el mando remoto está bloqueado por hardware (M13)."""
    if client_manager.is_disabled:
        return False # En modo simulado no bloqueamos por defecto
    
    lock_data = read_coils_safe(PLC_REMOTE_LOCK_ADDR, count=1)
    return lock_data.bits[0] if lock_data else False

# =========================================================================
# ZONA 3: RUTA PRINCIPAL (FRONTEND)
# =========================================================================
@api_bp.route('/')
def index():
    # Solo decimos conectado si el socket está abierto Y no estamos en modo deshabilitado
    is_online = client_manager.is_connected() and not client_manager.is_disabled
    status = "Conectado" if is_online else "Simulado"
    system_data = get_system_data()
    return render_template('index.html', 
                           usuario="Operador", 
                           rol="supervisor", 
                           status=status,
                           **system_data)

# =========================================================================
# ZONA 4: API MODBUS BASICA (COILS Y REGISTERS)
# =========================================================================
@api_bp.route('/read_coil', methods=['GET'])
def read_coil():
    try:
        address = int(request.args.get('address'))
        result = read_coils_safe(address, count=1)
        if not result: 
            if client_manager.is_disabled:
                return jsonify({'success': True, 'value': mock_read_coil(address)})
            return jsonify({'success': False, 'error': 'Fallo lectura (PLC offline o timeout)'}), 503
        return jsonify({'success': True, 'value': result.bits[0]})
    except Exception as e: 
        logger.error(f"Error en read_coil: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/write_coil', methods=['POST'])
def write_coil():
    try:
        data = request.get_json()
        address = data['address']
        value = bool(data['value'])
        
        if check_remote_lock():
            return jsonify({'success': False, 'error': 'Bloqueo Remoto Activo (Mantenimiento)'}), 403

        if client_manager.is_disabled:
            mock_write_coil(address, value)
            return jsonify({'success': True})

        result = write_coil_safe(address, value)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo escritura (PLC offline o timeout)'}), 503
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en write_coil: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/read_register', methods=['GET'])
def read_register():
    try:
        address = int(request.args.get('address'))
        if client_manager.is_disabled:
            return jsonify({'success': True, 'value': mock_read_register(address)})

        result = read_registers_safe(address, count=1)
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo lectura (PLC offline o timeout)'}), 503
        return jsonify({'success': True, 'value': result.registers[0]})
    except Exception as e: 
        logger.error(f"Error en read_register: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/write_register', methods=['POST'])
def write_register():
    try:
        data = request.get_json()
        address = data['address']
        value = int(data['value']) 
        
        if check_remote_lock():
            return jsonify({'success': False, 'error': 'Bloqueo Remoto Activo (Mantenimiento)'}), 403

        if client_manager.is_disabled:
            mock_write_register(address, value)
            return jsonify({'success': True})

        # Proteccion: 300 y 400 son coils de seguridad
        if address == 300 or address == 400: 
             return jsonify({'success': False, 'error': 'Dirección reservada para supervisor.'}), 403

        result = write_register_safe(address, value)
        
        if not result: 
            return jsonify({'success': False, 'error': 'Fallo escritura (PLC offline o timeout)'}), 503
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en write_register: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

# =========================================================================
# ZONA 5: API DE ESTADO (MONITOREO GENERAL)
# =========================================================================
@api_bp.route('/status')
def status():
    if client_manager.is_disabled:
        data = get_mock_status()
        data["mode"] = "Simulado"
        return jsonify(data)

    # 0. Verificar Bloqueo Remoto
    lock_data = read_coils_safe(PLC_REMOTE_LOCK_ADDR, count=1)
    remote_lock = lock_data.bits[0] if lock_data else False

    # 1. Lectura Coils
    coils_data = read_coils_safe(0, count=24)
    if not coils_data:
        return jsonify({'success': False, 'error': 'No se pudo conectar con el PLC o timeout de lectura'}), 503

    # Encender calentamiento de resistencia
    estado_t4  = read_coils_safe(350, count=1)
    estado_t2  = read_coils_safe(450, count=1)

    coils_in = coils_data.bits[:14]
    coils_out = coils_data.bits[14:24]

    pid_flags = {
        "t4_activo":  estado_t4.bits[0] if estado_t4 else False,
        "t2_activo":  estado_t2.bits[0] if estado_t2 else False
    }

    # 2. Analogicos
    ai = read_registers_safe(200, count=6)
    aq = read_registers_safe(301, count=5)
    reg_in = ai.registers if ai else [0]*6
    reg_out = aq.registers if aq else [0]*5
    
    # 3. SetPoints de Nivel
    sp_niv = read_registers_safe(101, count=5)
    sp_niveles = sp_niv.registers if sp_niv else [0]*5

    # 4. PIDs
    pid_t2_raw = read_registers_safe(400, count=8)
    pid_t2 = {}
    if pid_t2_raw:
        r = pid_t2_raw.registers
        pid_t2 = {
            'params': {'setpoint': round((r[0]*75/1000)+0.5, 1), 
                        'kp':    r[2]*0.01, 
                        'ti': r[4]*0.1, 
                        'td': r[6]*0.1},
            'status': {'temp_actual': round((r[1]*75/1000)+0.5, 1), 
                        'error': round(r[3]*75/1000, 1), 
                        'salida': r[5]/100.0}
        }

    pid_t4_raw = read_registers_safe(420, count=8)
    pid_t4 = {}
    if pid_t4_raw:
        r = pid_t4_raw.registers
        pid_t4 = {
            'params': {
                'setpoint': round((r[0]*75/1000)+0.5, 1), 
                'kp': r[2]*0.01, 
                'ti': r[4]*0.1, 
                'td': r[6]*0.1
                },
            'status': {
                'temp_actual': round((r[1]*75/1000)+0.5, 1), 
                'error': round(r[3]*75/1000, 1), 
                'salida': r[5]/100.0
                }
        }

    # Determinar modo para el frontend
    mode = "Conectado" if client_manager.is_connected() and not client_manager.is_disabled else "Simulado"

    # 5. Modos Auto/Manual (201-205)
    modes_data = read_coils_safe(201, count=5)
    tank_modes = modes_data.bits if modes_data else [False]*5

    return jsonify({
        "mode": mode,
        "remote_lock": remote_lock,
        "tank_modes": tank_modes,
        "coils_inputs": coils_in, 
        "coils_outputs": coils_out, 
        "pid_flags": pid_flags,
        "registers_inputs": reg_in, 
        "registers_outputs": reg_out, 
        "sp_niveles": sp_niveles,
        "pid_t2": pid_t2, 
        "pid_t4": pid_t4
    })

# =========================================================================
# ZONA 5.1: API DE CONFIGURACION (ESTATICA)
# =========================================================================
@api_bp.route('/data', methods=['GET'])
def get_data():
    """Devuelve la estructura de elementos del sistema."""
    try:
        return jsonify(get_system_data())
    except Exception as e:
        logger.error(f"Error en get_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =========================================================================
# ZONA 6: API CONTROL PID
# =========================================================================
@api_bp.route('/update_pid', methods=['POST'])
def update_pid():
    if client_manager.is_disabled:
        return jsonify({'success': True, 'note': 'Simulado'})
    try:
        d = request.get_json()
        base = 400 if d.get('id') == 'T2' else 420
        sp_raw = int(((float(d['setpoint']) - 0.5) * 1000) / 75)
        kp_raw = int(float(d['kp']) / 0.01)
        ti_raw = int(float(d['ti']) / 0.1)
        td_raw = int(float(d['td']) / 0.1)
        
        if check_remote_lock():
            return jsonify({'success': False, 'error': 'Bloqueo Remoto Activo (Mantenimiento)'}), 403

        r1 = write_register_safe(base, sp_raw)
        r2 = write_register_safe(base+2, kp_raw)
        r3 = write_register_safe(base+4, ti_raw)
        r4 = write_register_safe(base+6, td_raw)
        
        if not all([r1, r2, r3, r4]):
            return jsonify({'success': False, 'error': 'Fallo escritura parcial o total en PLC'}), 503

        logger.info(f"✓ PID {d.get('id')} actualizado")
        return jsonify({'success': True})
    except Exception as e: 
        logger.error(f"Error en update_pid: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/reset_pid', methods=['POST'])
def reset_pid(): 
    logger.info("Reset PID solicitado")
    return jsonify({'success': True})

@api_bp.route('/toggle_auto', methods=['POST'])
def toggle_auto():
    """Cambia entre modo Manual y Auto para un tanque."""
    if check_remote_lock():
        return jsonify({'success': False, 'error': 'Bloqueo Remoto Activo'}), 403
        
    try:
        data = request.get_json()
        address = int(data['address'])
        value = bool(data['value'])
        
        if client_manager.is_disabled:
            mock_write_coil(address, value)
            return jsonify({'success': True})
            
        result = write_coil_safe(address, value)
        if not result:
            return jsonify({'success': False, 'error': 'Fallo en PLC'}), 503
            
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error en toggle_auto: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/mock/toggle_input', methods=['POST'])
def mock_toggle_input():
    if not client_manager.is_disabled:
        return jsonify({"success": False, "error": "Not in simulation mode"}), 403
    
    try:
        data = request.get_json()
        address = int(data['address'])
        from mocks import mock_read_coil, mock_write_coil
        current = mock_read_coil(address)
        mock_write_coil(address, not current)
        return jsonify({"success": True, "new_state": not current})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
