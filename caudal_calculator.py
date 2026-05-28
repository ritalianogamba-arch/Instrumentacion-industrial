import time
import threading
from config.plc import PLC_SENDS_SCALED_LAB, raw_to_level_percent
from config.tanks import TANQUE_4
from config.logging_cfg import logger
from modbus_core import read_registers_safe, write_register_safe

def run_caudal_calculator():
    """Hilo secundario que calcula el caudal Q_int si el PLC no lo envía escalado."""
    logger.info("Iniciando calculador de caudal en background (PID LAB)...")
    
    last_level_pct = None
    
    while True:
        try:
            # Importación local en caso de que cambie en caliente
            from config.plc import PLC_SENDS_SCALED_LAB as sends_scaled
            
            # Si el PLC ya envía el caudal calculado, este hilo no debe escribir nada.
            if sends_scaled:
                time.sleep(1.0)
                continue
                
            # 1. Leer nivel actual del Tanque 4
            address_t4 = TANQUE_4.sensor_de_presion
            res = read_registers_safe(address_t4, count=1)
            
            if res and not res.isError():
                raw_level = res.registers[0]
                current_level_pct = raw_to_level_percent(raw_level, TANQUE_4.min_val, TANQUE_4.max_val)
                
                # 2. Calcular delta (derivada)
                if last_level_pct is not None:
                    delta_pct = current_level_pct - last_level_pct
                    dt = 1.0 # El hilo corre cada 1 segundo exacto
                    
                    # 3. Fórmula del Caudal (Q_int)
                    # Q_int := 0.0829 * (0.75/100.0) * (delta_pct / dt) * 1000.0 * 100.0;
                    q_int = 0.0829 * (0.75/100.0) * (delta_pct / dt) * 1000.0 * 100.0
                    
                    # Convertir a entero (puede ser negativo si delta es negativo)
                    q_int_raw = int(round(q_int))
                    
                    # Si es negativo, aplicamos complemento a 2 para 16-bits (Modbus Holding Register)
                    if q_int_raw < 0:
                        q_int_raw = (1 << 16) + q_int_raw
                    
                    # Evitamos desbordamientos de 16 bits
                    q_int_raw = max(0, min(65535, q_int_raw))
                    
                    # 4. Escribir en memoria 468 (Entrada del PID LAB)
                    write_register_safe(468, q_int_raw)
                    
                last_level_pct = current_level_pct
            
        except Exception as e:
            logger.error(f"Error en calculador de caudal: {e}")
            
        time.sleep(1.0)
