import random 
import threading
import time
from config import (
    SENSOR_TEMP_T2, SENSOR_TEMP_T4, SENSOR_PRESION_T1, 
    SENSOR_PRESION_T2, SENSOR_PRESION_T3, SENSOR_PRESION_T4_T5,
    ELECTRO_VALVULA_1, ELECTRO_VALVULA_2, ELECTRO_VALVULA_3,
    ELECTRO_VALVULA_4, ELECTRO_VALVULA_5, ELECTRO_VALVULA_6,
    ELECTRO_VALVULA_7, ELECTRO_VALVULA_8,
    VFD, VALVULA_NEUMATICA, RESISTENCIA_T2, RESISTENCIA_T4
)

# =========================================================================
# ESTADO GLOBAL INDEXADO POR DIRECCIÓN MODBUS
# =========================================================================

_coils = {addr: False for addr in range(1000)}
_registers = {addr: 0 for addr in range(1000)}

# Inicialización de valores coherentes
_registers[SENSOR_TEMP_T2.address] = int(25.0 * 1000 / 75)
_registers[SENSOR_TEMP_T4.address] = int(30.0 * 1000 / 75)
_registers[SENSOR_PRESION_T1.address] = 5000
_registers[SENSOR_PRESION_T2.address] = 6000
_registers[SENSOR_PRESION_T3.address] = 7000
_registers[SENSOR_PRESION_T4_T5.address] = 8000

# Setpoints nivel (4000 = 0%, 10000 = 100%)
for addr in range(101, 106):
    _registers[addr] = 7000 # 50%

# PID Setpoints iniciales
_registers[400] = int(25.0 * 1000 / 75)
_registers[420] = int(30.0 * 1000 / 75)

# Flags de simulación adicionales
_mock_state_flags = {
    "t4_permiso": True,
    "t2_permiso": True,
    "simulated": True,
    "remote_lock": False # Podemos cambiarlo manualmente para pruebas
}

# Inicializar modos de tanque (M201-M205) en Manual (False)
for addr in range(201, 206):
    _coils[addr] = False

# Inicializar llave de bloqueo (M13)
_coils[13] = True

def get_mock_status():
    """Compila el estado actual en el formato que espera el frontend (api_routes.py)"""
    
    # Coils 0-23 (Lectura base en api_routes)
    coils_0_23 = [_coils[i] for i in range(24)]
    
    # Analog inputs 200-205 (Lectura base ai)
    reg_in = [_registers[i] for i in range(200, 206)]
    
    # Analog outputs 301-305 (Lectura base aq - ajustada para incluir Res T4)
    reg_out = [_registers[i] for i in range(301, 306)]
    
    # Setpoints nivel 101-105
    sp_niveles_raw = [_registers[i] for i in range(101, 106)]
    sp_porcentajes = [int(max(0, min(100, (v - 4000) / 6000 * 100))) for v in sp_niveles_raw]

    # PID T2 (400-407)
    r2 = [_registers[i] for i in range(400, 408)]
    pid_t2 = {
        'params': {
            'setpoint': round((r2[0]*75/1000)+0.5, 1), 
            'kp': round(r2[2]*0.01, 2), 
            'ti': round(r2[4]*0.1, 1), 
            'td': round(r2[6]*0.1, 1)
        },
        'status': {
            'temp_actual': round((r2[1]*75/1000)+0.5, 1), 
            'error': round(r2[3]*75/1000, 1), 
            'salida': round(r2[5]/100.0, 2)
        }
    }

    # PID T4 (420-427)
    r4 = [_registers[i] for i in range(420, 428)]
    pid_t4 = {
        'params': {
            'setpoint': round((r4[0]*75/1000)+0.5, 1), 
            'kp': round(r4[2]*0.01, 2), 
            'ti': round(r4[4]*0.1, 1), 
            'td': round(r4[6]*0.1, 1)
        },
        'status': {
            'temp_actual': round((r4[1]*75/1000)+0.5, 1), 
            'error': round(r4[3]*75/1000, 1), 
            'salida': round(r4[5]/100.0, 2)
        }
    }

    # Modos de tanque (201-205)
    tank_modes = [_coils[i] for i in range(201, 206)]

    return {
        "coils_inputs": coils_0_23[:14],
        "coils_outputs": coils_0_23[14:24],
        "remote_lock": _coils[13],
        "tank_modes": tank_modes,
        "pid_flags": {
            "t4_activo": _coils[350],
            "t2_activo": _coils[450],
            "t4_permiso": _mock_state_flags["t4_permiso"],
            "t2_permiso": _mock_state_flags["t2_permiso"]
        },
        "registers_inputs": reg_in,
        "registers_outputs": reg_out,
        "sp_niveles": sp_porcentajes,
        "pid_t2": pid_t2,
        "pid_t4": pid_t4,
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
# HILO DE FISICAS (SIMULADOR DE CASCADA ACTUALIZADO)
# =========================================================================

def physics_loop():
    while True:
        try:
            # 1. SALIDAS ANALÓGICAS (ACTUADORES)
            # VFD=302, Neum=303, ResT2=304, ResT4=305
            vfd_p = max(0, min(100, (_registers[VFD.address] - 4000) / 16000 * 100))
            neum_p = max(0, min(100, (_registers[VALVULA_NEUMATICA.address] - 4000) / 16000 * 100))
            
            flujo_in = (vfd_p / 100) * (neum_p / 100) * 8.0 # Flujo un poco más rápido
            
            # 2. LÓGICA DE VÁLVULAS (ENTRADA FÍSICA O COMANDO SCADA)
            # Cada válvula responde a su botón físico (I0.X) o al mando del servidor (M14+X)
            def esta_abierta(ev_config, coil_idx):
                # El bloqueo remoto (M13) suele impedir el mando del servidor, 
                # pero el botón físico (I0.X) suele ser cableado directo o bypass.
                # Para la simulación: Bloqueo activo = ignorar comandos SCADA.
                cmd_scada = _coils[ev_config.entrada_server] and not _coils[13]
                btn_fisico = _coils[ev_config.entrada_digital]
                return cmd_scada or btn_fisico

            ev1 = esta_abierta(ELECTRO_VALVULA_1, 0)
            ev2 = esta_abierta(ELECTRO_VALVULA_2, 1)
            ev3 = esta_abierta(ELECTRO_VALVULA_3, 2)
            ev4 = esta_abierta(ELECTRO_VALVULA_4, 3)
            ev5 = esta_abierta(ELECTRO_VALVULA_5, 4)
            ev6 = esta_abierta(ELECTRO_VALVULA_6, 5)
            ev7 = esta_abierta(ELECTRO_VALVULA_7, 6)
            ev8 = esta_abierta(ELECTRO_VALVULA_8, 7)
            
            # Sincronizar bobinas de salida (%Q / Coils 14-21) para que el SCADA las lea
            _coils[14] = ev1; _coils[15] = ev2; _coils[16] = ev3; _coils[17] = ev4
            _coils[18] = ev5; _coils[19] = ev6; _coils[20] = ev7; _coils[21] = ev8
            
            # 3. NIVELES ACTUALES (CONVERSIÓN DE CRUDA A %)
            n_t1 = max(0, min(100, (_registers[SENSOR_PRESION_T1.address] - 4000) / 6000 * 100))
            n_t2 = max(0, min(100, (_registers[SENSOR_PRESION_T2.address] - 4000) / 6000 * 100))
            n_t3 = max(0, min(100, (_registers[SENSOR_PRESION_T3.address] - 4000) / 6000 * 100))
            n_t4_t5 = max(0, min(100, (_registers[SENSOR_PRESION_T4_T5.address] - 4000) / 6000 * 100))
            
            # 4. DINÁMICA DE LLENADO/VACIADO
            # Cascada 1: T1 -> T2 -> T3
            if ev1: n_t1 += flujo_in
            if ev3 and n_t1 > 5:
                n_t1 -= 5.0
                n_t2 += 5.0
            if ev4 and n_t2 > 5:
                n_t2 -= 5.0
                n_t3 += 5.0
            if ev7 and n_t3 > 0:
                n_t3 -= 4.0
                
            # Cascada 2: T4/T5 Acoplados
            if ev2: n_t4_t5 += flujo_in
            if ev8: n_t4_t5 += flujo_in * 0.5 # Entrada secundaria
            if ev6 and n_t4_t5 > 0: n_t4_t5 -= 4.0
            if ev5 and n_t4_t5 > 0: n_t4_t5 -= 4.0
            
            # 5.1 SIMULACION DE CONTROL DE NIVEL PLC (SI ESTA EN AUTO)
            # Tanques 1-5 usan SP en 101-105 y Modos en 201-205
            niveles = [n_t1, n_t2, n_t3, n_t4_t5, n_t4_t5]
            for i in range(5):
                if _coils[201 + i]: # Si está en AUTO
                    sp_raw = _registers[101 + i]
                    sp_p = max(0, min(100, (sp_raw - 4000) / 6000 * 100))
                    
                    # Control simple tipo On/Off con histéresis para simular PLC
                    if niveles[i] < sp_p - 1:
                        niveles[i] += 2.0 # Llenando en auto
                    elif niveles[i] > sp_p + 1:
                        niveles[i] -= 2.0 # Vaciando en auto
            
            n_t1, n_t2, n_t3, n_t4_t5 = niveles[0], niveles[1], niveles[2], niveles[3]

            # 5. CLAMPING Y RESTRICCIONES
            n_t1 = max(0, min(100, n_t1))
            n_t2 = max(20.0, min(100, n_t2)) # Seguridad de 20%
            n_t3 = max(0, min(100, n_t3))
            n_t4_t5 = max(20.0, min(100, n_t4_t5)) # Seguridad de 20%
            
            # 6. FISICA DE CONTROL PID (SIMULADA)
            def simular_pid(pid_idx, addr_sp, addr_pv, addr_res, coil_enable):
                if _coils[coil_enable]:
                    sp = (_registers[addr_sp] * 75 / 1000) + 0.5
                    pv = (_registers[addr_pv] * 75 / 1000) + 0.5
                    error = sp - pv
                    # Control proporcional simple para la simulación
                    output = max(0, min(1.0, error * 0.2)) 
                    _registers[addr_res] = int(4000 + (output * 16000))
                else:
                    # Si el PID está OFF, la resistencia vuelve a 4000 (0%)
                    _registers[addr_res] = 4000

            simular_pid(1, 400, SENSOR_TEMP_T2.address, 300, 450)
            simular_pid(2, 420, SENSOR_TEMP_T4.address, 301, 350)

            # 7. TEMPERATURAS (CONVERSIÓN DE CRUDA A °C)
            t2_temp = (_registers[SENSOR_TEMP_T2.address] * 75 / 1000) + 0.5
            t4_temp = (_registers[SENSOR_TEMP_T4.address] * 75 / 1000) + 0.5
            
            p_res_t2 = (_registers[300] - 4000) / 16000
            p_res_t4 = (_registers[301] - 4000) / 16000
            
            t2_temp = max(20.0, t2_temp - 0.05)
            t4_temp = max(20.0, t4_temp - 0.05)
            
            if ev3: t2_temp = t2_temp + (20 - t2_temp) * 0.15
            if ev2: t4_temp = t4_temp + (20 - t4_temp) * 0.15
            
            if n_t2 > 20: t2_temp += (p_res_t2 * 1.5)
            if n_t4_t5 > 20: t4_temp += (p_res_t4 * 1.5)
            
            # Sincronizar registros
            _registers[SENSOR_TEMP_T2.address] = int((t2_temp - 0.5) * 1000 / 75)
            _registers[SENSOR_TEMP_T4.address] = int((t4_temp - 0.5) * 1000 / 75)
            _registers[401] = _registers[SENSOR_TEMP_T2.address]
            _registers[421] = _registers[SENSOR_TEMP_T4.address]

        except Exception as e:
            pass
        time.sleep(0.5)

# Iniciar hilo de físicas
threading.Thread(target=physics_loop, daemon=True).start()
