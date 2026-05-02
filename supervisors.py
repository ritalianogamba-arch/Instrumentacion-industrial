import time
from config import logger
from modbus_core import read_registers_safe, write_coil_safe

# =========================================================================
# ZONA 7: SUPERVISORES DE SEGURIDAD (SOLO NIVEL)
# =========================================================================

# --- SUPERVISOR TACHO 2 ---
def supervisor_tacho_2():
    logger.info("Supervisor T2 (%M400 Nivel) iniciado")
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
            
            # Escritura forzada (Heartbeat)
            write_coil_safe(ADDR_PERM, permiso)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error en supervisor T2: {e}")
            time.sleep(5)

# --- SUPERVISOR TACHO 4 ---
def supervisor_tacho_4():
    logger.info("Supervisor T4 (%M300 Nivel) iniciado")
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
            
            # Escritura forzada (Heartbeat)
            write_coil_safe(ADDR_PERM, permiso)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error en supervisor T4: {e}")
            time.sleep(5)
