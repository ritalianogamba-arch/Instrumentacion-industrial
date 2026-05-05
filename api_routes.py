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

    # 1. Obtener datos del sistema para saber qué leer
    system_data = get_system_data()
    elementos = system_data["elementos"]

    # 2. Lectura de Coils (Entradas y Válvulas)
    # Leemos un bloque que cubra la mayoría para optimizar
    coils_data = read_coils_safe(0, count=500)
    
    def get_coil(addr):
        return coils_data.bits[addr] if coils_data and addr < len(coils_data.bits) else False

    coils_in = [get_coil(b['address']) for b in elementos['botones_ev']]
    coils_out = [get_coil(v['entrada_server']) for v in elementos['valvulas']]

    # 3. Analogicos (Sensores y Actuadores)
    reg_in = []
    for s in elementos['sensores']:
        res = read_registers_safe(s['address'], count=1)
        reg_in.append(res.registers[0] if res else 0)

    reg_out = []
    for a in elementos['salidas_analogicas']:
        res = read_registers_safe(a['address'], count=1)
        reg_out.append(res.registers[0] if res else 0)
    
    # 4. SetPoints de Nivel y Modos Auto
    sp_niveles = []
    tank_modes = []
    for t in elementos['tanques']:
        res_sp = read_registers_safe(t['SetPoint_Level'], count=1)
        sp_niveles.append(res_sp.registers[0] if res_sp else 0)
        tank_modes.append(get_coil(t['modo_auto_address']))

    # 5. PIDs (Lectura dinámica por PID)
    pids_status = {}
    pid_flags = {}
    for pid in elementos['pids']:
        res = read_registers_safe(pid['address_set_point'], count=8)
        if res:
            r = res.registers
            pids_status[f"pid_{pid['identifier']}"] = {
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
        
        # Flags de activación (usando el botón virtual address del modelo)
        pid_flags[f"t{2 if pid['identifier'] == 1 else 4}_activo"] = get_coil(pid['boton_virtual_address'])

    mode = "Conectado" if client_manager.is_connected() and not client_manager.is_disabled else "Simulado"
    remote_lock = get_coil(PLC_REMOTE_LOCK_ADDR)

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
        "pid_t2": pids_status.get("pid_1", {}), 
        "pid_t4": pids_status.get("pid_2", {}),
        "elementos": elementos
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
        pid_id_str = d.get('id') # 'T2' o 'T4'
        
        # Encontrar el PID en la configuración
        system_data = get_system_data()
        pid_obj = next((p for p in system_data["elementos"]["pids"] if p['nombre'].split()[-1] == pid_id_str), None)
        
        if not pid_obj:
            return jsonify({'success': False, 'error': f'PID {pid_id_str} no encontrado'}), 404
            
        base = pid_obj['address_set_point']
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

        logger.info(f"✓ PID {pid_id_str} actualizado en base {base}")
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
