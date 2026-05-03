from flask import Flask, request, jsonify, render_template
from pymodbus.client import ModbusTcpClient
import time
import threading 

app = Flask(__name__)

# =========================================================================
# ZONA 1: CONFIGURACION PLC Y CLIENTE
# =========================================================================
PLC_IP = '192.168.1.10'
PLC_PORT = 502
client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

try:
    client.connect()
    if client.is_socket_open():
        print(f"Conexion inicial Modbus establecida con {PLC_IP}:{PLC_PORT}")
    else:
        print(f"Fallo en la conexion inicial con {PLC_IP}:{PLC_PORT}")
except Exception as e:
    print(f"Excepcion al intentar conexion inicial: {e}")

# =========================================================================
# ZONA 2: FUNCION DE ROBUSTEZ (CONEXION SEGURA)
# =========================================================================
def safe_modbus_operation(operation_func, **kwargs):
    global client
    try:
        if not client.is_socket_open():
            client.connect() 
            if not client.is_socket_open():
                print("Fallo la reconexion Modbus.")
                return None 

        result = operation_func(**kwargs)
        if result and result.isError():
             return None
        return result
    
    except Exception as e:
        print(f"[safe_modbus_operation] Error: {e}. Reintentando...")
        try:
            client.close()
            time.sleep(0.1) 
            client.connect()
            if client.is_socket_open():
                print("[safe_modbus_operation] Reconexion exitosa. Reintentando operacion...")
                result = operation_func(**kwargs)
                if result and result.isError():
                    return None
                return result
            else:
                print("[safe_modbus_operation] Fallo en la reconexion. Operacion cancelada.")
                return None
        except Exception as e_retry:
            print(f"[safe_modbus_operation] Fallo critico en el reintento: {e_retry}")
            return None

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
        result = safe_modbus_operation(client.read_coils, address=address, count=1)
        if not result: return jsonify({'success': False, 'error': 'Fallo lectura'})
        return jsonify({'success': True, 'value': result.bits[0]})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

@app.route('/write_coil', methods=['POST'])
def write_coil():
    try:
        data = request.get_json()
        address = data['address']
        value = bool(data['value'])
        result = safe_modbus_operation(client.write_coil, address=address, value=value)
        if not result: return jsonify({'success': False, 'error': 'Fallo escritura'})
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

@app.route('/read_register', methods=['GET'])
def read_register():
    try:
        address = int(request.args.get('address'))
        result = safe_modbus_operation(client.read_holding_registers, address=address, count=1)
        if not result: return jsonify({'success': False, 'error': 'Fallo lectura'})
        return jsonify({'success': True, 'value': result.registers[0]})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

@app.route('/write_register', methods=['POST'])
def write_register():
    try:
        data = request.get_json()
        address = data['address']
        value = int(data['value']) 
        # Proteccion: 300 y 400 son coils de seguridad
        if address == 300 or address == 400: 
             return jsonify({'success': False, 'error': 'Direccion reservada para supervisor.'})
        result = safe_modbus_operation(client.write_register, address=address, value=value)
        if not result: return jsonify({'success': False, 'error': 'Fallo escritura'})
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

# =========================================================================
# ZONA 5: API DE ESTADO (MONITOREO GENERAL)
# =========================================================================
@app.route('/status')
def status():
    # 1. Lectura Coils
    coils_data = safe_modbus_operation(client.read_coils, address=0, count=24)
    permiso_t4 = safe_modbus_operation(client.read_coils, address=300, count=1)
    estado_t4  = safe_modbus_operation(client.read_coils, address=350, count=1)
    permiso_t2 = safe_modbus_operation(client.read_coils, address=400, count=1)
    estado_t2  = safe_modbus_operation(client.read_coils, address=450, count=1)

    coils_in = coils_data.bits[:14] if coils_data else [False]*14
    coils_out = coils_data.bits[14:24] if coils_data else [False]*10

    pid_flags = {
        "t4_permiso": permiso_t4.bits[0] if permiso_t4 else False,
        "t4_activo":  estado_t4.bits[0] if estado_t4 else False,
        "t2_permiso": permiso_t2.bits[0] if permiso_t2 else False,
        "t2_activo":  estado_t2.bits[0] if estado_t2 else False
    }

    # 2. Analogicos
    ai = safe_modbus_operation(client.read_holding_registers, address=200, count=6)
    aq = safe_modbus_operation(client.read_holding_registers, address=301, count=4)
    reg_in = ai.registers if ai else [0]*6
    reg_out = aq.registers if aq else [0]*4
    
    # 3. SetPoints de Nivel
    sp_niv = safe_modbus_operation(client.read_holding_registers, address=101, count=5)
    sp_niveles = sp_niv.registers if sp_niv else [0]*5

    # 4. PIDs
    pid_t2_raw = safe_modbus_operation(client.read_holding_registers, address=400, count=8)
    pid_t2 = {}
    if pid_t2_raw:
        r = pid_t2_raw.registers
        pid_t2 = {
            'params': {'setpoint': round((r[0]*75/1000)+0.5, 1), 'kp': r[2]*0.01, 'ti': r[4]*0.1, 'td': r[6]*0.1},
            'status': {'temp_actual': round((r[1]*75/1000)+0.5, 1), 'error': round(r[3]*75/1000, 1), 'salida': r[5]/100.0}
        }

    pid_t4_raw = safe_modbus_operation(client.read_holding_registers, address=420, count=8)
    pid_t4 = {}
    if pid_t4_raw:
        r = pid_t4_raw.registers
        pid_t4 = {
            'params': {'setpoint': round((r[0]*75/1000)+0.5, 1), 'kp': r[2]*0.01, 'ti': r[4]*0.1, 'td': r[6]*0.1},
            'status': {'temp_actual': round((r[1]*75/1000)+0.5, 1), 'error': round(r[3]*75/1000, 1), 'salida': r[5]/100.0}
        }

    return jsonify({
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
        
        safe_modbus_operation(client.write_register, address=base, value=sp_raw)
        safe_modbus_operation(client.write_register, address=base+2, value=kp_raw)
        safe_modbus_operation(client.write_register, address=base+4, value=ti_raw)
        safe_modbus_operation(client.write_register, address=base+6, value=td_raw)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

@app.route('/reset_pid', methods=['POST'])
def reset_pid(): return jsonify({'success': True})

# =========================================================================
# ZONA 7: SUPERVISORES DE SEGURIDAD (SOLO NIVEL)
# =========================================================================

# --- SUPERVISOR TACHO 2 ---
def supervisor_tacho_2():
    print("Hilo T2 (%M400 Nivel) iniciado.")
    ADDR_NIV=204; ADDR_PERM=400
    MIN_RAW=7000
    
    while True:
        try:
            r_n = safe_modbus_operation(client.read_holding_registers, address=ADDR_NIV, count=1)
            permiso = False
            
            if r_n:
                niv = r_n.registers[0]
                # SOLO VERIFICA NIVEL
                if niv > MIN_RAW:
                    permiso = True
                    # print(f"[T2] Nivel OK: {niv}")
                else:
                    permiso = False
                    # print(f"[T2] Nivel BAJO: {niv}")

            # Escritura forzada (Heartbeat)
            safe_modbus_operation(client.write_coil, address=ADDR_PERM, value=permiso)
            time.sleep(1)
        except: time.sleep(5)

# --- SUPERVISOR TACHO 4 ---
def supervisor_tacho_4():
    print("Hilo T4 (%M300 Nivel) iniciado.")
    ADDR_NIV=203; ADDR_PERM=300
    MIN_RAW=6300
    
    while True:
        try:
            r_n = safe_modbus_operation(client.read_holding_registers, address=ADDR_NIV, count=1)
            permiso = False
            
            if r_n:
                niv = r_n.registers[0]
                # SOLO VERIFICA NIVEL
                if niv > MIN_RAW:
                    permiso = True
                    # print(f"[T4] Nivel OK: {niv}")
                else:
                    permiso = False
                    # print(f"[T4] Nivel BAJO: {niv}")

            # Escritura forzada (Heartbeat)
            safe_modbus_operation(client.write_coil, address=ADDR_PERM, value=permiso)
            time.sleep(1)
        except: time.sleep(5)

if __name__ == '__main__':
    t2_thread = threading.Thread(target=supervisor_tacho_2, daemon=True)
    t4_thread = threading.Thread(target=supervisor_tacho_4, daemon=True)
    t2_thread.start()
    t4_thread.start()
    try: app.run(host='0.0.0.0', port=8080, ssl_context=('server.crt', 'server.key'), debug=True)
    except: app.run(host='0.0.0.0', port=8080, debug=True)