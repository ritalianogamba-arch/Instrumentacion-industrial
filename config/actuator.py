from models.iot_models import SalidaAnalogica

# =========================================================================
# ENTRADAS DIGITALES
# =========================================================================

# Nota: 
# %MW HOLDING REGISTER 

# TODO(tano): AÑADIR AL PLC las 2 resistencias
RESISTENCIA_T2 = SalidaAnalogica(nombre='Resistencia Tanque 2',address=304, estado=None, min_val=4000, max_val=20000, unidad='%')
RESISTENCIA_T4 = SalidaAnalogica(nombre='Resistencia Tanque 4',address=305, estado=None, min_val=4000, max_val=20000, unidad='%')
VALVULA_NEUMATICA = SalidaAnalogica(nombre='Valvula Neumatica',address=303, estado=None, min_val=4000, max_val=20000, unidad='%') 
VFD = SalidaAnalogica(nombre='Variador de frecuencia',address=302, estado=None, min_val=4000, max_val=20000, unidad='Hz')         
