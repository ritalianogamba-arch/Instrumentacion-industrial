from models.iot_models import BotonVirtual
from models.iot_models import EntradaDigital

# =========================================================================
# BOTONES VIRTUALES (SCADA -> PLC)
# =========================================================================

# Modos de Grupos (Manual/Auto)
BTN_GRUPO_A = BotonVirtual(nombre="Modo Auto Grupo A", address=20)
BTN_GRUPO_B = BotonVirtual(nombre="Modo Auto Grupo B", address=21)

# Comandos de Válvulas desde SCADA
BTN_VALVULA_1 = BotonVirtual(nombre="Abrir/Cerrar EV1", address=1)
BTN_VALVULA_2 = BotonVirtual(nombre="Abrir/Cerrar EV2", address=2)
BTN_VALVULA_3 = BotonVirtual(nombre="Abrir/Cerrar EV3", address=3)
BTN_VALVULA_4 = BotonVirtual(nombre="Abrir/Cerrar EV4", address=4)
BTN_VALVULA_5 = BotonVirtual(nombre="Abrir/Cerrar EV5", address=5)
BTN_VALVULA_6 = BotonVirtual(nombre="Abrir/Cerrar EV6", address=6)
BTN_VALVULA_7 = BotonVirtual(nombre="Abrir/Cerrar EV7", address=7)
BTN_VALVULA_8 = BotonVirtual(nombre="Abrir/Cerrar EV8", address=8)

# Comandos PID
BTN_PID_T2 = BotonVirtual(nombre="Activar PID T2", address=321)
BTN_PID_T4 = BotonVirtual(nombre="Activar PID T4", address=341)

# =========================================================================
# ENTRADAS VIRTUALES
# =========================================================================
BOTON_EV_1 = EntradaDigital(nombre='Boton EV 1',address=0, estado=None)
BOTON_EV_2 = EntradaDigital(nombre='Boton EV 2',address=1, estado=None)
BOTON_EV_3 = EntradaDigital(nombre='Boton EV 3',address=2, estado=None)
BOTON_EV_4 = EntradaDigital(nombre='Boton EV 4',address=3, estado=None)
BOTON_EV_5 = EntradaDigital(nombre='Boton EV 5',address=4, estado=None)
BOTON_EV_6 = EntradaDigital(nombre='Boton EV 6',address=5, estado=None)
BOTON_EV_7 = EntradaDigital(nombre='Boton EV 7',address=6, estado=None)
BOTON_EV_8 = EntradaDigital(nombre='Boton EV 8',address=7, estado=None)
LLAVE_MANDO_REMOTO = EntradaDigital(nombre='Llave Mando Remoto', address=13, estado=None)

