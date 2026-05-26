from blinker.base import F
from . import addresses

# PLC Connection Settings
PLC_IP = '192.168.1.10'
PLC_PORT = 502
MODBUS_TIMEOUT = 1
MODBUS_RETRIES = 1
PLC_REMOTE_LOCK_ADDR = addresses.LLAVE_MANDO_REMOTO

# =========================================================================
# ESCALAMIENTO DE TEMPERATURA  (Sensor analógico → °C)
# =========================================================================
#
# El PLC debe ejecutar la siguiente ecuación en el bloque de programa
# que lee la entrada analógica del sensor de temperatura (ej. PT100/NTC):
#
#   ┌─────────────────────────────────────────────────────────────┐
#   │  Temp_°C = (RAW_ADC * 75 / 1000) + 0.5                    │
#   │                                                             │
#   │  Donde:                                                     │
#   │    RAW_ADC  = Valor crudo del conversor A/D  (0 … ~1333)    │
#   │    75/1000  = Factor de escala del sensor                   │
#   │    0.5      = Offset de calibración                         │
#   │                                                             │
#   │  Ejemplo:  RAW_ADC = 600                                    │
#   │            Temp_°C = (600 * 75 / 1000) + 0.5 = 45.5 °C     │
#   │                                                             │
#   │  El resultado (Temp_°C) se escribe en el %MW correspondiente│
#   │  como un entero (ej. 45) o x10 si se necesita 1 decimal    │
#   │  (ej. 455 = 45.5°C).                                       │
#   └─────────────────────────────────────────────────────────────┘
#
# Cuando PLC_SENDS_SCALED_TEMP = True, el SCADA asume que el %MW
# ya contiene el valor en °C y NO aplica ninguna conversión.
PLC_SENDS_SCALED_TEMP = False   

def raw_to_celsius(raw_value: int) -> float:
    """Convierte un valor raw del PLC a grados Celsius.
    
    Si PLC_SENDS_SCALED_TEMP=False (actual): aplica la fórmula de escalamiento.
    Si PLC_SENDS_SCALED_TEMP=True (futuro):  el valor ya es °C, solo lo redondea.
    """
    if PLC_SENDS_SCALED_TEMP:
        return round(float(raw_value), 1)
    return round((raw_value * 75 / 1000) + 0.5, 1)

# =========================================================================
# ESCALAMIENTO DE NIVEL (Sensores de presión → % de llenado)
# =========================================================================
# Cambiar a True cuando el PLC implemente el escalamiento internamente.
# En ese caso:
#   - Los sensores ya envían el nivel en porcentaje (0-100%)
#   - Los set-points de nivel se deben enviar en porcentaje (0-100)
PLC_SENDS_SCALED_LEVEL = True

def raw_to_level_percent(raw: int, cfg_min: int, cfg_max: int) -> float:
    """Convierte valor raw del sensor de presión a porcentaje de nivel (0-100).
    
    Si PLC_SENDS_SCALED_LEVEL=False: aplica la fórmula raw→% usando min/max del tanque.
    Si PLC_SENDS_SCALED_LEVEL=True:  el valor ya es %, solo lo clampea.
    """
    if PLC_SENDS_SCALED_LEVEL:
        return round(max(0.0, min(100.0, float(raw))), 1)
    if cfg_max == cfg_min:
        return 0.0
    p = ((raw - cfg_min) / (cfg_max - cfg_min)) * 100
    return round(max(0.0, min(100.0, p)), 1)

def percent_to_level_raw(percent: float, cfg_min: int, cfg_max: int) -> int:
    """Convierte porcentaje de nivel (0-100) a valor raw para escribir el SP en el PLC.
    
    Si PLC_SENDS_SCALED_LEVEL=False: escala al rango raw del PLC (ej. 4000-10000).
    Si PLC_SENDS_SCALED_LEVEL=True:  envía el porcentaje directamente.
    """
    p = max(0.0, min(100.0, float(percent)))
    if PLC_SENDS_SCALED_LEVEL:
        return int(round(p))
    return int(round(cfg_min + (p * (cfg_max - cfg_min) / 100)))
