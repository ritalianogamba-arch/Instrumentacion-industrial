from models.iot_models import BotonVirtual
from models.iot_models import EntradaDigital
from . import addresses

# =========================================================================
# BOTONES VIRTUALES (SCADA -> PLC)
# =========================================================================

# Modos de Grupos (Manual/Auto)
BTN_GRUPO_A = BotonVirtual(nombre="Modo Auto Grupo A", address=addresses.BTN_GRUPO_A)
BTN_GRUPO_B = BotonVirtual(nombre="Modo Auto Grupo B", address=addresses.BTN_GRUPO_B)

# Comandos de Válvulas desde SCADA
BTN_VALVULA_1 = BotonVirtual(nombre="Abrir/Cerrar EV1", address=addresses.BTN_VALVULA_1)
BTN_VALVULA_2 = BotonVirtual(nombre="Abrir/Cerrar EV2", address=addresses.BTN_VALVULA_2)
BTN_VALVULA_3 = BotonVirtual(nombre="Abrir/Cerrar EV3", address=addresses.BTN_VALVULA_3)
BTN_VALVULA_4 = BotonVirtual(nombre="Abrir/Cerrar EV4", address=addresses.BTN_VALVULA_4)
BTN_VALVULA_5 = BotonVirtual(nombre="Abrir/Cerrar EV5", address=addresses.BTN_VALVULA_5)
BTN_VALVULA_6 = BotonVirtual(nombre="Abrir/Cerrar EV6", address=addresses.BTN_VALVULA_6)
BTN_VALVULA_7 = BotonVirtual(nombre="Activar PID T7", address=addresses.BTN_VALVULA_7)
BTN_VALVULA_8 = BotonVirtual(nombre="Abrir/Cerrar EV8", address=addresses.BTN_VALVULA_8)

# Comandos PID
BTN_PID_T2 = BotonVirtual(nombre="Activar PID T2", address=addresses.BTN_PID_T2)
BTN_PID_T4 = BotonVirtual(nombre="Activar PID T4", address=addresses.BTN_PID_T4)

# =========================================================================
# ENTRADAS DIGITALES MONITOREADAS
# =========================================================================
# NOTA: Las entradas físicas del PLC (%I0.x) se copian a estas direcciones
# de memoria (%M 30-38) para que el SCADA pueda monitorearlas
BOTON_EV_1 = EntradaDigital(nombre='Boton EV 1', address=addresses.BOTON_EV_1, estado=None)
BOTON_EV_2 = EntradaDigital(nombre='Boton EV 2', address=addresses.BOTON_EV_2, estado=None)
BOTON_EV_3 = EntradaDigital(nombre='Boton EV 3', address=addresses.BOTON_EV_3, estado=None)
BOTON_EV_4 = EntradaDigital(nombre='Boton EV 4', address=addresses.BOTON_EV_4, estado=None)
BOTON_EV_5 = EntradaDigital(nombre='Boton EV 5', address=addresses.BOTON_EV_5, estado=None)
BOTON_EV_6 = EntradaDigital(nombre='Boton EV 6', address=addresses.BOTON_EV_6, estado=None)
BOTON_EV_7 = EntradaDigital(nombre='Boton EV 7', address=addresses.BOTON_EV_7, estado=None)
BOTON_EV_8 = EntradaDigital(nombre='Boton EV 8', address=addresses.BOTON_EV_8, estado=None)
BOTON_VN = EntradaDigital(nombre='Boton VN', address=addresses.BOTON_VN, estado=None)
LLAVE_MANDO_REMOTO = EntradaDigital(nombre='Llave Mando Remoto', address=addresses.LLAVE_MANDO_REMOTO, estado=None)
