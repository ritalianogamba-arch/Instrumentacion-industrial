import threading
import time
import os
import math
from config import (
    LISTA_BOTONES_EV, LISTA_SENSORES, LISTA_VALVULAS, LISTA_TANQUES, LISTA_PIDS, LISTA_ACTUADORES,
    logger, raw_to_celsius
)

# =========================================================================
# MEMORIA CENTRALIZADA DEL SIMULADOR (VERSIÓN VISUAL / OFFLINE)
# =========================================================================
class MockMemory:
    def __init__(self):
        self.coils = {addr: False for addr in range(10000)}
        self.registers = {addr: 0 for addr in range(10000)}
        
        # Inicialización base de niveles y actuadores a 4000 (0%)
        for addr in [s.address for s in LISTA_SENSORES if "PRESION" in s.nombre] + [a.address for a in LISTA_ACTUADORES]:
            self.registers[addr] = 4000
            
        # Inicialización base de temperatura a 20°C
        for addr in [s.address for s in LISTA_SENSORES if "Temperatura" in s.nombre]:
            self.registers[addr] = int((20.0 - 0.5) * 1000 / 75)
            
        self.physics = {
            "levels": {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
            "temp_cycle": 20.0,
            "temp_direction": 1 # 1 para subir, -1 para bajar
        }

store = MockMemory()

def get_mock_status():
    from config import get_system_data
    system_data = get_system_data()
    
    def get_pid_data(pid_obj, current_temp_raw):
        base = pid_obj.address_set_point
        r = [store.registers.get(base + i, 0) for i in range(8)]
        return {
            'params': {
                'setpoint': raw_to_celsius(r[0]),
                'kp': 2.5, 'ti': 15.0, 'td': 1.0
            },
            'status': {
                'temp_actual': raw_to_celsius(current_temp_raw),
                'error': 0.0, 'salida': 0.0
            }
        }

    # Sincronizar todos los sensores en el orden exacto de config/sensors.py
    # 0: Temp T2 (201), 1: Temp T4 (200), 2: Pres T1 (202), 3: Pres T2 (204), 4: Pres T3 (205), 5: Pres T4_T5 (203)
    sensores_raw = []
    for s in system_data["elementos"]["sensores"]:
        sensores_raw.append(store.registers.get(s['address'], 0))

    return {
        "mode": "Simulado",
        "elementos": system_data["elementos"],
        "remote_lock": store.coils.get(13, False), 
        "tank_modes": [store.coils.get(t.modo_auto_address, False) for t in LISTA_TANQUES],
        "coils_inputs": [store.coils.get(b.address, False) for b in LISTA_BOTONES_EV],
        "coils_outputs": [store.coils.get(v.entrada_server, False) for v in LISTA_VALVULAS],
        "registers_inputs": sensores_raw,
        "registers_outputs": [store.registers.get(a.address, 0) for a in LISTA_ACTUADORES],
        "sp_niveles": [store.registers.get(t.SetPoint_Level, 0) for t in LISTA_TANQUES],
        "pid_t2": get_pid_data(LISTA_PIDS[0], store.registers.get(LISTA_PIDS[0].address_set_point + 1, 260)),
        "pid_t4": get_pid_data(LISTA_PIDS[1], store.registers.get(LISTA_PIDS[1].address_set_point + 1, 260)),
        "pid_flags": {
            "t2_activo": store.coils.get(LISTA_PIDS[0].boton_virtual_address, False),
            "t4_activo": store.coils.get(LISTA_PIDS[1].boton_virtual_address, False)
        }
    }

def mock_write_coil(address, value):
    store.coils[address] = bool(value)
    return True

def mock_read_coil(address):
    return store.coils.get(address, False)

def mock_write_register(address, value):
    store.registers[address] = int(value)
    return True

def mock_read_register(address):
    return store.registers.get(address, 0)

# =========================================================================
# MOTOR DE FÍSICAS (DINÁMICA GRÁFICA Y SIMULACIÓN)
# =========================================================================

def physics_loop():
    last_time = time.time()
    while True:
        try:
            now = time.time()
            dt = max(0.01, min(0.5, now - last_time))
            last_time = now
            
            locked = store.coils.get(13, False)
            v = {}
            for valve in LISTA_VALVULAS:
                v[valve.entrada_server] = store.coils.get(valve.entrada_server, False) and not locked
                if valve.entrada_digital:
                    v[valve.entrada_digital] = store.coils.get(valve.entrada_digital, False) or v.get(valve.entrada_server, False)

            # 1. RAMPA DE TEMPERATURA CONTINUA (20°C a 95°C)
            # Para visualizar el gradiente de color dinámicamente
            speed_temp = 5.0 * dt # 5 grados por segundo
            store.physics["temp_cycle"] += speed_temp * store.physics["temp_direction"]
            
            if store.physics["temp_cycle"] >= 95.0:
                store.physics["temp_cycle"] = 95.0
                store.physics["temp_direction"] = -1
            elif store.physics["temp_cycle"] <= 20.0:
                store.physics["temp_cycle"] = 20.0
                store.physics["temp_direction"] = 1

            raw_temp = int((store.physics["temp_cycle"] - 0.5) * 1000 / 75)
            
            for s in LISTA_SENSORES:
                if "Temperatura" in s.nombre:
                    store.registers[s.address] = raw_temp
            # Simular temperatura actual también en el registro 1 del PID (Temp Actual)
            for p in LISTA_PIDS:
                store.registers[p.address_set_point + 1] = raw_temp

            # 2. MOVIMIENTO DE AGUA INDEPENDIENTE (COMO PLANTAS INDIVIDUALES)
            flow_speed_in = 3.0 * dt  # Llenado suavizado
            flow_speed_out = 1.5 * dt  # Vaciado suavizado
            l = store.physics["levels"]
            
            for i, tank in enumerate(LISTA_TANQUES):
                idx = i + 1
                llenando = False
                vaciando = False
                
                # Llenado dependiente de válvula superior y vaciado de válvula inferior
                for valve in LISTA_VALVULAS:
                    if valve.address == tank.valvula_superior:
                        if store.coils.get(valve.entrada_server, False) or store.coils.get(valve.entrada_digital, False):
                            llenando = True
                    if valve.address == tank.valvula_inferior:
                        if store.coils.get(valve.entrada_server, False) or store.coils.get(valve.entrada_digital, False):
                            vaciando = True
                
                if llenando: 
                    l[idx] += flow_speed_in
                
                if vaciando:
                    l[idx] -= flow_speed_out
                
                l[idx] = max(0.0, min(100.0, l[idx]))

            # Sincronizar niveles a registros Modbus dinámicamente
            for i, tank in enumerate(LISTA_TANQUES):
                idx = i + 1
                store.registers[tank.sensor_de_presion] = int(4000 + (l[idx] * 160))


        except Exception as e:
            logger.error(f"Error en física simulada: {e}")
        time.sleep(0.05)

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not os.environ.get('WERKZEUG_RUN_MAIN'):
    threading.Thread(target=physics_loop, daemon=True, name="SimEngine").start()
