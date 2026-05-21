from models.iot_models import EntradaAnalogica
from . import addresses

# =========================================================================
# ENTRADAS ANALOGICAS
# =========================================================================
SENSOR_TEMP_T2 = EntradaAnalogica(nombre= 'Temperatura Tanque 2',address=addresses.SENSOR_TEMP_T2, estado=None)
SENSOR_TEMP_T4 = EntradaAnalogica(nombre= 'Temperatura Tanque 4',address=addresses.SENSOR_TEMP_T4, estado=None)

SENSOR_PRESION_T1 = EntradaAnalogica(nombre= 'PRESION Tanque 1',address=addresses.SENSOR_PRESION_T1, estado=None)
SENSOR_PRESION_T2 = EntradaAnalogica(nombre= 'PRESION Tanque 2 ',address=addresses.SENSOR_PRESION_T2, estado=None)
SENSOR_PRESION_T3 = EntradaAnalogica(nombre= 'PRESION Tanque 3',address=addresses.SENSOR_PRESION_T3, estado=None)
SENSOR_PRESION_T4_T5 = EntradaAnalogica(nombre= 'PRESION Tanque 4 y 5',address=addresses.SENSOR_PRESION_T4_T5, estado=None)
