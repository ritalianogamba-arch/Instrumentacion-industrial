from dataclasses import asdict
 
from .sensors import * 
from .valves import * 
from .tanks import * 
from .pid import * 
from .actuator import *
from .virtual_buttons import *

LISTA_BOTONES_EV = [
    BOTON_EV_1, BOTON_EV_2, BOTON_EV_3, BOTON_EV_4, 
    BOTON_EV_5, BOTON_EV_6, BOTON_EV_7, BOTON_EV_8,
    LLAVE_MANDO_REMOTO
]
LISTA_SENSORES = [SENSOR_TEMP_T2, SENSOR_TEMP_T4, SENSOR_PRESION_T1, SENSOR_PRESION_T2, SENSOR_PRESION_T3, SENSOR_PRESION_T4_T5]
LISTA_VALVULAS = [ELECTRO_VALVULA_1, ELECTRO_VALVULA_2, ELECTRO_VALVULA_3, ELECTRO_VALVULA_4, ELECTRO_VALVULA_5, ELECTRO_VALVULA_6, ELECTRO_VALVULA_7, ELECTRO_VALVULA_8]
LISTA_TANQUES = [TANQUE_1, TANQUE_2, TANQUE_3, TANQUE_4, TANQUE_5]
LISTA_PIDS = [PID_T2, PID_T4]
LISTA_ACTUADORES = [RESISTENCIA_T2,RESISTENCIA_T4, VALVULA_NEUMATICA, VFD]
LISTA_BOTONES_VIRTUALES = [
    BTN_GRUPO_A, BTN_GRUPO_B,
    BTN_VALVULA_1, BTN_VALVULA_2, BTN_VALVULA_3, BTN_VALVULA_4,
    BTN_VALVULA_5, BTN_VALVULA_6, BTN_VALVULA_7, BTN_VALVULA_8,
    BTN_PID_T2, BTN_PID_T4
]

def get_system_data():
    return {
        "elementos": {
            "botones_ev": [asdict(b) for b in LISTA_BOTONES_EV],
            "sensores": [asdict(s) for s in LISTA_SENSORES],
            "valvulas": [asdict(v) for v in LISTA_VALVULAS],
            "tanques": [asdict(t) for t in LISTA_TANQUES],
            "pids": [asdict(p) for p in LISTA_PIDS],
            "salidas_analogicas": [asdict(a) for a in LISTA_ACTUADORES],
            "botones_virtuales": [asdict(bv) for bv in LISTA_BOTONES_VIRTUALES]
        }
    }
