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
    nombre='Tacho 1',
    sensor_de_presion=SENSOR_PRESION_T1.address,
    valvula_superior=ELECTRO_VALVULA_1.address,
    valvula_inferior=ELECTRO_VALVULA_3.address,
    SetPoint_Level=101,
    modo_auto_address=201,
    boton_virtual_address=201
)

TANQUE_2: Tanque = Tanque(
    nombre='Tacho 2',
    sensor_de_presion=SENSOR_PRESION_T2.address,
    valvula_superior=ELECTRO_VALVULA_3.address,
    valvula_inferior=ELECTRO_VALVULA_4.address,
    SetPoint_Level=102,
    modo_auto_address=202,
    boton_virtual_address=202,
    sensor_de_temperatura=SENSOR_TEMP_T2.address,
    resistencia=RESISTENCIA_T2.address,
    condicion_de_nivel= 400,
    pid_id= 1
)

TANQUE_3: Tanque = Tanque(   
    nombre= 'Tanque 3',
    sensor_de_presion=SENSOR_PRESION_T3.address,            
    valvula_superior=ELECTRO_VALVULA_4.address,            
    valvula_inferior=ELECTRO_VALVULA_7.address, 
    SetPoint_Level= 103,           
    modo_auto_address= 203,
    boton_virtual_address=203
)   

TANQUE_4: Tanque = Tanque(   
    nombre= 'Tanque 4',
    sensor_de_presion=SENSOR_PRESION_T4_T5.address,         
    sensor_de_temperatura=SENSOR_TEMP_T4.address,   
    valvula_superior=ELECTRO_VALVULA_2.address,           
    valvula_inferior=ELECTRO_VALVULA_6.address,    
    condicion_de_nivel= 300, # Valor de %M COIL
    resistencia = RESISTENCIA_T4.address,
    pid_id= 2,
    SetPoint_Level= 104, 
    modo_auto_address= 204,
    boton_virtual_address=204
)   

TANQUE_5: Tanque = Tanque(
    nombre='Tacho 5',
    sensor_de_presion=SENSOR_PRESION_T4_T5.address,
    valvula_superior=ELECTRO_VALVULA_8.address,
    valvula_inferior=ELECTRO_VALVULA_5.address,
    SetPoint_Level=105,
    modo_auto_address=205,
    boton_virtual_address=205
)
