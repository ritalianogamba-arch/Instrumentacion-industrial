from models.iot_models import EntradaAnalogica
from . import addresses

# =========================================================================
# ENTRADAS ANALOGICAS
# =========================================================================
SENSOR_TEMP_T2 = EntradaAnalogica(nombre= 'Temperatura Tanque 2',address=addresses.SENSOR_TEMP_T2, estado=None)
SENSOR_TEMP_T4 = EntradaAnalogica(nombre= 'Temperatura Tanque 4',address=addresses.SENSOR_TEMP_T4, estado=None)

SENSOR_PRESION_T1 = EntradaAnalogica(nombre= 'Nivel Tanque 1',address=addresses.SENSOR_PRESION_T1, estado=None)
SENSOR_PRESION_T2 = EntradaAnalogica(nombre= 'Nivel Tanque 2 ',address=addresses.SENSOR_PRESION_T2, estado=None)
SENSOR_PRESION_T3 = EntradaAnalogica(nombre= 'Nivel Tanque 3',address=addresses.SENSOR_PRESION_T3, estado=None)
SENSOR_PRESION_T4 = EntradaAnalogica(nombre= 'Nivel Tanque 4',address=addresses.SENSOR_PRESION_T4, estado=None)
