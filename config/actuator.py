from models.iot_models import SalidaAnalogica
from . import addresses

# =========================================================================
# ENTRADAS DIGITALES
# =========================================================================

# Nota: 
# %MW HOLDING REGISTER 

# TODO(tano): AÑADIR AL PLC las 2 resistencias
RESISTENCIA_T2 = SalidaAnalogica(nombre='Resistencia Tanque 2',address=addresses.RESISTENCIA_T2, estado=None, min_val=4000, max_val=20000, unidad='%')
RESISTENCIA_T4 = SalidaAnalogica(nombre='Resistencia Tanque 4',address=addresses.RESISTENCIA_T4, estado=None, min_val=4000, max_val=20000, unidad='%')
VALVULA_NEUMATICA = SalidaAnalogica(nombre='Valvula Neumatica',address=addresses.VALVULA_NEUMATICA, estado=None, min_val=4000, max_val=20000, unidad='%') 
VFD = SalidaAnalogica(nombre='Variador de frecuencia',address=addresses.VFD, estado=None, min_val=4000, max_val=20000, unidad='Hz')         
