from models.iot_models import Tanque
from .sensors import (
    SENSOR_PRESION_T1, SENSOR_PRESION_T2, SENSOR_PRESION_T3, 
    SENSOR_PRESION_T4_T5, SENSOR_TEMP_T2, SENSOR_TEMP_T4
)
from .valves import (
    ELECTRO_VALVULA_1, ELECTRO_VALVULA_2, ELECTRO_VALVULA_3, 
    ELECTRO_VALVULA_4, ELECTRO_VALVULA_5, ELECTRO_VALVULA_6, 
    ELECTRO_VALVULA_7, ELECTRO_VALVULA_8
)

from .actuator import (
    RESISTENCIA_T2,
    RESISTENCIA_T4
)

# =========================================================================
# TANQUES
# =========================================================================

# NOTA:
# (%MW) Asociado a (%IW)

TANQUE_1: Tanque = Tanque(
    nombre='Tanque 1',
    sensor_de_presion=SENSOR_PRESION_T1.address,
    valvula_superior=ELECTRO_VALVULA_1.address,
    valvula_inferior=ELECTRO_VALVULA_3.address,
    valvula_superior_identificador=1,
    valvula_inferior_identificador=3,
    SetPoint_Level=101,
    modo_auto_address=201,
    boton_virtual_address=201,
    altura=1.8,
    diametro=0.8,
    volumen=0.9,
    material="Polietileno",
    lado_controles="izq",
    lado_termometro="der"
)

TANQUE_2: Tanque = Tanque(
    nombre='Tanque 2',
    sensor_de_presion=SENSOR_PRESION_T2.address,
    valvula_superior=ELECTRO_VALVULA_3.address,
    valvula_inferior=ELECTRO_VALVULA_4.address,
    valvula_superior_identificador=3,
    valvula_inferior_identificador=4,
    SetPoint_Level=102,
    modo_auto_address=202,
    boton_virtual_address=202,
    sensor_de_temperatura=SENSOR_TEMP_T2.address,
    resistencia=RESISTENCIA_T2.address,
    condicion_de_nivel= 400,
    pid_id= 1,
    altura=2.5,
    diametro=1.2,
    volumen=2.8,
    material="Acero Inox",
    lado_controles="izq",
    lado_termometro="der"
)

TANQUE_3: Tanque = Tanque(   
    nombre= 'Tanque 3',
    sensor_de_presion=SENSOR_PRESION_T3.address,            
    valvula_superior=ELECTRO_VALVULA_4.address,            
    valvula_inferior=ELECTRO_VALVULA_7.address, 
    valvula_superior_identificador=4,
    valvula_inferior_identificador=7,
    SetPoint_Level= 103,           
    modo_auto_address= 203,
    boton_virtual_address=203,
    altura=2.0,
    diametro=1.0,
    volumen=1.5,
    material="Acero Inox",
    lado_controles="izq",
    lado_termometro="der"
)   

TANQUE_4: Tanque = Tanque(   
    nombre= 'Tanque 4',
    sensor_de_presion=SENSOR_PRESION_T4_T5.address,         
    sensor_de_temperatura=SENSOR_TEMP_T4.address,   
    valvula_superior=ELECTRO_VALVULA_2.address,           
    valvula_inferior=ELECTRO_VALVULA_6.address,    
    valvula_superior_identificador=2,
    valvula_inferior_identificador=6,
    condicion_de_nivel= 300, # Valor de %M COIL
    resistencia = RESISTENCIA_T4.address,
    pid_id= 2,
    SetPoint_Level= 104, 
    modo_auto_address= 204,
    boton_virtual_address=204,
    altura=3.0,
    diametro=1.5,
    volumen=5.3,
    material="Acero Inox",
    lado_controles="der",
    lado_termometro="izq"
)   

TANQUE_5: Tanque = Tanque(
    nombre='Tanque 5',
    sensor_de_presion=SENSOR_PRESION_T4_T5.address,
    valvula_superior=ELECTRO_VALVULA_8.address,
    valvula_inferior=ELECTRO_VALVULA_5.address,
    valvula_superior_identificador=8,
    valvula_inferior_identificador=5,
    SetPoint_Level=105,
    modo_auto_address=205,
    boton_virtual_address=205,
    altura=2.2,
    diametro=1.1,
    volumen=2.1,
    material="Fibra de Vidrio",
    lado_controles="der",
    lado_termometro="izq"
)
