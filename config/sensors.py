from models.iot_models import EntradaAnalogica

# =========================================================================
# ENTRADAS ANALOGICAS
# =========================================================================
SENSOR_TEMP_T2 = EntradaAnalogica(nombre= 'Temperatura Tanque 2',address=302, estado=None)
SENSOR_TEMP_T4 = EntradaAnalogica(nombre= 'Temperatura Tanque 4',address=304, estado=None)

SENSOR_PRESION_T1 = EntradaAnalogica(nombre= 'PRESION Tanque 1',address=201, estado=None)
SENSOR_PRESION_T2 = EntradaAnalogica(nombre= 'PRESION Tanque 2 ',address=202, estado=None)
SENSOR_PRESION_T3 = EntradaAnalogica(nombre= 'PRESION Tanque 3',address=203, estado=None)
SENSOR_PRESION_T4_T5 = EntradaAnalogica(nombre= 'PRESION Tanque 4 y 5',address=204, estado=None)
