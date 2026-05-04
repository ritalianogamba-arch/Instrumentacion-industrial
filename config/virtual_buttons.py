from models.iot_models import BotonVirtual

# =========================================================================
# BOTONES VIRTUALES (SCADA -> PLC)
# =========================================================================

# Modos de Tanque (Manual/Auto)
BTN_AUTO_T1 = BotonVirtual(nombre="Modo Auto T1", address=201)
BTN_AUTO_T2 = BotonVirtual(nombre="Modo Auto T2", address=202)
BTN_AUTO_T3 = BotonVirtual(nombre="Modo Auto T3", address=203)
BTN_AUTO_T4 = BotonVirtual(nombre="Modo Auto T4", address=204)
BTN_AUTO_T5 = BotonVirtual(nombre="Modo Auto T5", address=205)

# Comandos de Válvulas desde SCADA
BTN_VALVULA_1 = BotonVirtual(nombre="Abrir/Cerrar EV1", address=14)
BTN_VALVULA_2 = BotonVirtual(nombre="Abrir/Cerrar EV2", address=15)
BTN_VALVULA_3 = BotonVirtual(nombre="Abrir/Cerrar EV3", address=16)
BTN_VALVULA_4 = BotonVirtual(nombre="Abrir/Cerrar EV4", address=17)
BTN_VALVULA_5 = BotonVirtual(nombre="Abrir/Cerrar EV5", address=18)
BTN_VALVULA_6 = BotonVirtual(nombre="Abrir/Cerrar EV6", address=19)
BTN_VALVULA_7 = BotonVirtual(nombre="Abrir/Cerrar EV7", address=20)
BTN_VALVULA_8 = BotonVirtual(nombre="Abrir/Cerrar EV8", address=21)

# Comandos PID
BTN_PID_T2 = BotonVirtual(nombre="Activar PID T2", address=450)
BTN_PID_T4 = BotonVirtual(nombre="Activar PID T4", address=350)
