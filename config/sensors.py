from models.iot_models import EntradaAnalogica

# =========================================================================
# ENTRADAS ANALOGICAS
# =========================================================================
SENSOR_TEMP_T2 = EntradaAnalogica(address=201, estado=None)
SENSOR_TEMP_T4 = EntradaAnalogica(address=200, estado=None)

SENSOR_PRESION_T1 = EntradaAnalogica(address=202, estado=None)
SENSOR_PRESION_T2 = EntradaAnalogica(address=204, estado=None)
SENSOR_PRESION_T3 = EntradaAnalogica(address=205, estado=None)
SENSOR_PRESION_T4_T5 = EntradaAnalogica(address=203, estado=None)
