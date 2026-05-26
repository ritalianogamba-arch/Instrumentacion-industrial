from flask import Blueprint, request, jsonify, render_template
from config.logging_cfg import logger
from config.data import get_system_data
from config.plc import PLC_REMOTE_LOCK_ADDR, raw_to_celsius, PLC_SENDS_SCALED_TEMP, PLC_SENDS_SCALED_LEVEL
from config.addresses import BOTON_VN, VALVULA_NEUMATICA
from modbus_core import (
    read_coils_safe, write_coil_safe, 
    read_registers_safe, write_register_safe,
    client_manager
)
import mocks

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)

def check_remote_lock():
    """Verifica si el mando remoto está bloqueado por hardware."""
    if is_sim_mode():
        return mocks.mock_read_coil(PLC_REMOTE_LOCK_ADDR)
    lock_data = read_coils_safe(PLC_REMOTE_LOCK_ADDR, count=1)
    return lock_data.bits[0] if lock_data else False

def is_sim_mode():
    """True cuando no hay conexión real al PLC (modo simulación o desconectado)."""
    return client_manager.is_disabled or not client_manager.is_connected()

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
                           plc_sends_scaled_temp=PLC_SENDS_SCALED_TEMP,
                           plc_sends_scaled_level=PLC_SENDS_SCALED_LEVEL,
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
                return jsonify({'success': True, 'value': mocks.mock_read_coil(address)})
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

        if is_sim_mode():
            mocks.mock_write_coil(address, value)
            return jsonify({'success': True, 'note': 'Escrito en Mock'})

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
            return jsonify({'success': True, 'value': mocks.mock_read_register(address)})

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

        if is_sim_mode():
            mocks.mock_write_register(address, value)
            return jsonify({'success': True, 'note': 'Escrito en Mock'})

        # Proteccion: solo 300 es reservada para supervisor (salida hardware)
        if address == 300:
             return jsonify({'success': False, 'error': 'Dirección 300 reservada para supervisor.'}), 403

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
    # FORZAR MOCK SI NO HAY PLC
    if is_sim_mode():
        resp = jsonify(mocks.get_mock_status())
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp

    system_data = get_system_data()
    elementos = system_data["elementos"]

    # 2. Lectura de Coils (Entradas y Válvulas)
    # Leemos un bloque que cubra la mayoría para optimizar
    coils_data = read_coils_safe(0, count=500)
    
    def get_coil(addr):
        return coils_data.bits[addr] if coils_data and addr < len(coils_data.bits) else False

    coils_in = [get_coil(b['address']) for b in elementos['botones_ev']]
    coils_out = [get_coil(v['address']) for v in elementos['valvulas']]
    remote_lock = get_coil(PLC_REMOTE_LOCK_ADDR)

    # 3. Analogicos (Sensores y Actuadores)
    reg_in = []
    for s in elementos['sensores']:
        res = read_registers_safe(s['address'], count=1)
        reg_in.append(res.registers[0] if res else 0)

    reg_out = []
    for a in elementos['salidas_analogicas']:
        res = read_registers_safe(a['address'], count=1)
        reg_out.append(res.registers[0] if res else 0)

    # For maintenance/local manual mode, map BOTON_VN to pneumatic valve output
    if remote_lock:
        vn_button_idx = next((idx for idx, b in enumerate(elementos['botones_ev']) if b['address'] == BOTON_VN), None)
        pneumatica_idx = next((idx for idx, a in enumerate(elementos['salidas_analogicas']) if a['address'] == VALVULA_NEUMATICA), None)
        if vn_button_idx is not None and pneumatica_idx is not None and vn_button_idx < len(coils_in):
            vn_on = coils_in[vn_button_idx]
            min_val = elementos['salidas_analogicas'][pneumatica_idx].get('min_val', 4000)
            max_val = elementos['salidas_analogicas'][pneumatica_idx].get('max_val', 20000)
            reg_out[pneumatica_idx] = max_val if vn_on else min_val
    
    # 4. SetPoints de Nivel y Modos Auto
    sp_niveles = []
    tank_modes = []
    condiciones_nivel = []
    for t in elementos['tanques']:
        res_sp = read_registers_safe(t['SetPoint_Level'], count=1)
        sp_niveles.append(res_sp.registers[0] if res_sp else 0)
        tank_modes.append(1 if get_coil(t['modo_auto_address']) else 0)
        # Condición de nivel (coil 0/1) – si no está definida, usar 0 (seguro)
        addr_cond = t.get('condicion_de_nivel')
        if addr_cond:
            condiciones_nivel.append(1 if get_coil(addr_cond) else 0)
        else:
            condiciones_nivel.append(0)

    # 5. PIDs (Lectura dinámica por PID)
    pids_status = {}
    pid_flags = {}
    for pid in elementos['pids']:
        res = read_registers_safe(pid['address_set_point'], count=8)
        if res:
            r = res.registers
            pids_status[f"pid_{pid['identifier']}"] = {
                'params': {
                    'setpoint': raw_to_celsius(r[0]),
                    'kp': r[2]*0.01, 
                    'ti': r[4]*0.1, 
                    'td': r[6]*0.1
                },
                'status': {
                    'temp_actual': raw_to_celsius(r[1]),
                    'error': round(r[3]*75/1000, 1), 
                    'salida': r[5]/100.0
                }
            }
        
        # Flags de activación (usando el botón virtual address del modelo)
        pid_flags[f"t{2 if pid['identifier'] == 1 else 4}_activo"] = get_coil(pid['boton_virtual_address'])

    mode = "Conectado" if client_manager.is_connected() and not client_manager.is_disabled else "Simulado"

    # Eliminado mapeo de niveles_tanques redundante e incorrecto.

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
        "condiciones_nivel": condiciones_nivel,
        "pid_t2": pids_status.get("pid_1", None), 
        "pid_t4": pids_status.get("pid_2", None),
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
    if is_sim_mode():
        return jsonify({'success': True, 'note': 'Simulado (sin PLC)'})
    try:
        d = request.get_json()
        pid_id_str = d.get('id') # 'T2' o 'T4'
        
        # Encontrar el PID en la configuración
        system_data = get_system_data()
        pid_id_clean = pid_id_str.replace('T', '').strip()
        pid_obj = next((p for p in system_data["elementos"]["pids"] if p['nombre'].split()[-1] == pid_id_clean), None)
        
        if not pid_obj:
            return jsonify({'success': False, 'error': f'PID {pid_id_str} no encontrado'}), 404
            
        base = pid_obj['address_set_point']
        if PLC_SENDS_SCALED_TEMP:
            sp_raw = int(round(float(d['setpoint'])))
        else:
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
        
        if is_sim_mode():
            mocks.mock_write_coil(address, value)
            return jsonify({'success': True, 'note': 'Escrito en Mock'})
            
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
        return jsonify({"success": False, "error": "Solo disponible en modo simulación"}), 403
    
    try:
        data = request.get_json()
        address = int(data['address'])
        current = mocks.mock_read_coil(address)
        mocks.mock_write_coil(address, not current)
        return jsonify({"success": True, "new_state": not current})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@api_bp.route('/mock/set_register', methods=['POST'])
def mock_set_register():
    if not client_manager.is_disabled:
        return jsonify({"success": False, "error": "Solo disponible en modo simulación"}), 403
    
    try:
        data = request.get_json()
        address = int(data['address'])
        value = int(data['value'])
        mocks.mock_write_register(address, value)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@api_bp.route('/mock/set_coil', methods=['POST'])
def mock_set_coil():
    if not client_manager.is_disabled:
        return jsonify({"success": False, "error": "Solo disponible en modo simulación"}), 403
    
    try:
        data = request.get_json()
        address = int(data['address'])
        value = bool(data['value'])
        mocks.mock_write_coil(address, value)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
