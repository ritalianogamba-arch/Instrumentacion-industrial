import random 
import threading
import time
from config import (
    LISTA_BOTONES_EV, LISTA_SENSORES, LISTA_VALVULAS, LISTA_TANQUES, LISTA_PIDS, LISTA_ACTUADORES,
    SENSOR_TEMP_T2, SENSOR_TEMP_T4, SENSOR_PRESION_T1, 
    SENSOR_PRESION_T2, SENSOR_PRESION_T3, SENSOR_PRESION_T4_T5,
    ELECTRO_VALVULA_1, ELECTRO_VALVULA_2, ELECTRO_VALVULA_3,
    ELECTRO_VALVULA_4, ELECTRO_VALVULA_5, ELECTRO_VALVULA_6,
    ELECTRO_VALVULA_7, ELECTRO_VALVULA_8,
    VFD, VALVULA_NEUMATICA, RESISTENCIA_T2, RESISTENCIA_T4
)

_coils = {addr: False for addr in range(1000)}
_registers = {addr: 4000 for addr in range(1000)}

# Flags de simulación adicionales
_mock_state_flags = {
    "t4_permiso": True,
    "t2_permiso": True,
    "simulated": True,
    "remote_lock": False
}

# Inicializar actuadores para que haya flujo por defecto (ej. 12000 = ~50%)
_registers[VFD.address] = 12000
_registers[VALVULA_NEUMATICA.address] = 12000

# Inicializar modos de tanque y bloqueo
for t in LISTA_TANQUES:
    _coils[t.modo_auto_address] = False
    # Inicializar SetPoints a un valor por defecto (ej. 10000 = ~37%)
    _registers[t.SetPoint_Level] = 10000
    
_coils[13] = False # M13 Bloqueo Remoto (False = Desbloqueado para SCADA)

def get_mock_status():
    """Compila el estado actual para el frontend usando los modelos"""
    
    coils_in = [_coils[b.address] for b in LISTA_BOTONES_EV]
    coils_out = [_coils[v.entrada_server] for v in LISTA_VALVULAS]
    
    reg_in = [_registers[s.address] for s in LISTA_SENSORES]
    reg_out = [_registers[a.address] for a in LISTA_ACTUADORES]
    
    sp_niveles_raw = [_registers[t.SetPoint_Level] for t in LISTA_TANQUES]
    sp_porcentajes = [int(max(0, min(100, (v - 4000) / 6000 * 100))) for v in sp_niveles_raw]

    # Helper para compilar PID status
    def get_pid_data(pid_obj):
        r = [_registers[pid_obj.address_set_point + i] for i in range(8)]
        return {
            'params': {
                'setpoint': round((r[0]*75/1000)+0.5, 1), 
                'kp': round(r[2]*0.01, 2), 
                'ti': round(r[4]*0.1, 1), 
                'td': round(r[6]*0.1, 1)
            },
            'status': {
                'temp_actual': round((r[1]*75/1000)+0.5, 1), 
                'error': round(r[3]*75/1000, 1), 
                'salida': round(r[5]/100.0, 2)
            }
        }

    return {
        "coils_inputs": coils_in,
        "coils_outputs": coils_out,
        "remote_lock": _coils[13],
        "tank_modes": [_coils[t.modo_auto_address] for t in LISTA_TANQUES],
        "pid_flags": {
            "t4_activo": _coils[LISTA_PIDS[1].boton_virtual_address],
            "t2_activo": _coils[LISTA_PIDS[0].boton_virtual_address],
            "t4_permiso": _mock_state_flags["t4_permiso"],
            "t2_permiso": _mock_state_flags["t2_permiso"]
        },
        "registers_inputs": reg_in,
        "registers_outputs": reg_out,
        "sp_niveles": sp_porcentajes,
        "pid_t2": get_pid_data(LISTA_PIDS[0]),
        "pid_t4": get_pid_data(LISTA_PIDS[1]),
        "simulated": True
    }

def mock_write_coil(address, value):
    _coils[address] = bool(value)
    return True

def mock_read_coil(address):
    return _coils.get(address, False)

def mock_write_register(address, value):
    _registers[address] = int(value)
    return True

def mock_read_register(address):
    return _registers.get(address, 0)

# =========================================================================
# HILO DE FISICAS
# =========================================================================

def physics_loop():
    while True:
        try:
            # 1. SALIDAS ANALÓGICAS
            vfd_p = max(0, min(100, (_registers[VFD.address] - 4000) / 16000 * 100))
            neum_p = max(0, min(100, (_registers[VALVULA_NEUMATICA.address] - 4000) / 16000 * 100))
            flujo_in = (vfd_p / 100) * (neum_p / 100) * 8.0
            
            # 2. LÓGICA DE VÁLVULAS
            def esta_abierta(v_obj):
                cmd_scada = _coils[v_obj.entrada_server] and not _coils[13]
                btn_fisico = _coils[v_obj.entrada_digital]
                return cmd_scada or btn_fisico

            # Estado actual de válvulas
            evs = { i+1: esta_abierta(v) for i, v in enumerate(LISTA_VALVULAS) }
            
            # Sincronizar bobinas de salida (M14+)
            for i, v in enumerate(LISTA_VALVULAS):
                # Asumiendo que el SCADA espera ver el estado real en coils 14-21
                _coils[14 + i] = evs[i+1]
            
            # 3. NIVELES ACTUALES
            levels = {
                1: max(0, min(100, (_registers[SENSOR_PRESION_T1.address] - 4000) / 6000 * 100)),
                2: max(0, min(100, (_registers[SENSOR_PRESION_T2.address] - 4000) / 6000 * 100)),
                3: max(0, min(100, (_registers[SENSOR_PRESION_T3.address] - 4000) / 6000 * 100)),
                4: max(0, min(100, (_registers[SENSOR_PRESION_T4_T5.address] - 4000) / 6000 * 100))
            }
            
            # 4. DINÁMICA DE CASCADA
            if evs[1]: levels[1] += flujo_in
            if evs[3] and levels[1] > 5:
                levels[1] -= 5.0
                levels[2] += 5.0
            if evs[4] and levels[2] > 5:
                levels[2] -= 5.0
                levels[3] += 5.0
            if evs[7] and levels[3] > 0:
                levels[3] -= 4.0
                
            if evs[2]: levels[4] += flujo_in
            if evs[8]: levels[4] += flujo_in * 0.5
            if evs[6] and levels[4] > 0: levels[4] -= 4.0
            if evs[5] and levels[4] > 0: levels[4] -= 4.0
            
            # 5. CONTROL DE NIVEL AUTOMÁTICO
            for i, t in enumerate(LISTA_TANQUES):
                if _coils[t.modo_auto_address]:
                    sp_p = max(0, min(100, (_registers[t.SetPoint_Level] - 4000) / 6000 * 100))
                    curr = levels[4] if i >= 3 else levels[i+1]
                    if curr < sp_p - 1:
                        if i >= 3: levels[4] += 2.0
                        else: levels[i+1] += 2.0
                    elif curr > sp_p + 1:
                        if i >= 3: levels[4] -= 2.0
                        else: levels[i+1] -= 2.0
            
            # 6. SEGURIDAD Y CLAMPING
            levels[1] = max(0, min(100, levels[1]))
            levels[2] = max(20.0, min(100, levels[2]))
            levels[3] = max(0, min(100, levels[3]))
            levels[4] = max(20.0, min(100, levels[4]))

            # Sincronizar registros de presión
            _registers[SENSOR_PRESION_T1.address] = int(4000 + (levels[1] * 60))
            _registers[SENSOR_PRESION_T2.address] = int(4000 + (levels[2] * 60))
            _registers[SENSOR_PRESION_T3.address] = int(4000 + (levels[3] * 60))
            _registers[SENSOR_PRESION_T4_T5.address] = int(4000 + (levels[4] * 60))

            # 7. PID Y TEMPERATURA
            def simular_pid(pid_obj, res_addr, coil_enable):
                if _coils[coil_enable]:
                    sp = (_registers[pid_obj.address_set_point] * 75 / 1000) + 0.5
                    pv = (_registers[pid_obj.address_set_point + 1] * 75 / 1000) + 0.5
                    error = sp - pv
                    output = max(0, min(1.0, error * 0.2)) 
                    _registers[res_addr] = int(4000 + (output * 16000))
                    # Actualizar error y salida en registros de estado PID
                    _registers[pid_obj.address_set_point + 3] = int(error * 1000 / 75)
                    _registers[pid_obj.address_set_point + 5] = int(output * 100)
                else:
                    _registers[res_addr] = 4000
                    _registers[pid_obj.address_set_point + 5] = 0

            simular_pid(LISTA_PIDS[0], 300, LISTA_PIDS[0].boton_virtual_address) # T2
            simular_pid(LISTA_PIDS[1], 301, LISTA_PIDS[1].boton_virtual_address) # T4

            # 8. EVOLUCIÓN TÉRMICA
            t2_temp = (_registers[SENSOR_TEMP_T2.address] * 75 / 1000) + 0.5
            t4_temp = (_registers[SENSOR_TEMP_T4.address] * 75 / 1000) + 0.5
            
            p_res_t2 = (_registers[300] - 4000) / 16000
            p_res_t4 = (_registers[301] - 4000) / 16000
            
            t2_temp = max(20.0, t2_temp - 0.05)
            t4_temp = max(20.0, t4_temp - 0.05)
            
            if evs[3]: t2_temp += (20 - t2_temp) * 0.15
            if evs[2]: t4_temp += (20 - t4_temp) * 0.15
            
            if levels[2] > 20: t2_temp += (p_res_t2 * 1.5)
            if levels[4] > 20: t4_temp += (p_res_t4 * 1.5)
            
            _registers[SENSOR_TEMP_T2.address] = int((t2_temp - 0.5) * 1000 / 75)
            _registers[SENSOR_TEMP_T4.address] = int((t4_temp - 0.5) * 1000 / 75)
            # Sincronizar PV del PID
            _registers[LISTA_PIDS[0].address_set_point + 1] = _registers[SENSOR_TEMP_T2.address]
            _registers[LISTA_PIDS[1].address_set_point + 1] = _registers[SENSOR_TEMP_T4.address]

        except Exception as e:
            pass
        time.sleep(0.5)

# Iniciar hilo de físicas
threading.Thread(target=physics_loop, daemon=True).start()
