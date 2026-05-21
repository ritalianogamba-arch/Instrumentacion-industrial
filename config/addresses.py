# =========================================================================
# MAPA CENTRAL DE DIRECCIONES MODBUS
# =========================================================================
# Todas las direcciones (Coils, Input Registers, Holding Registers) deben
# configurarse aquí para evitar hardcoding y tener un único punto de verdad.

# -------------------------------------------------------------------------
# BOTONES VIRTUALES (COILS - Write)
# -------------------------------------------------------------------------
BTN_VALVULA_1 = 1
BTN_VALVULA_2 = 2
BTN_VALVULA_3 = 3
BTN_VALVULA_4 = 4
BTN_VALVULA_5 = 5
BTN_VALVULA_6 = 6
BTN_VALVULA_7 = 7
BTN_VALVULA_8 = 8

BTN_GRUPO_A = 20
BTN_GRUPO_B = 21

BTN_PID_T2 = 321
BTN_PID_T4 = 341

# -------------------------------------------------------------------------
# ENTRADAS DIGITALES MONITOREADAS (COILS - Read)
# (Botones físicos copiados a %M por el PLC)
# -------------------------------------------------------------------------
BOTON_EV_1 = 30
BOTON_EV_2 = 31
BOTON_EV_3 = 32
BOTON_EV_4 = 33
BOTON_EV_5 = 34
BOTON_EV_6 = 35
BOTON_EV_7 = 36
BOTON_EV_8 = 37

LLAVE_MANDO_REMOTO = 38

# -------------------------------------------------------------------------
# ELECTRO VALVULAS - SALIDAS DIGITALES (COILS - Write)
# -------------------------------------------------------------------------
ELECTRO_VALVULA_1 = 100
ELECTRO_VALVULA_2 = 101
ELECTRO_VALVULA_3 = 102
ELECTRO_VALVULA_4 = 103
ELECTRO_VALVULA_5 = 104
ELECTRO_VALVULA_6 = 105
ELECTRO_VALVULA_7 = 106
ELECTRO_VALVULA_8 = 107

# -------------------------------------------------------------------------
# SENSORES (INPUT REGISTERS - Read)
# -------------------------------------------------------------------------
SENSOR_PRESION_T1 = 201
SENSOR_PRESION_T2 = 202
SENSOR_PRESION_T3 = 203
SENSOR_PRESION_T4_T5 = 204

SENSOR_TEMP_T2 = 302
SENSOR_TEMP_T4 = 304

# -------------------------------------------------------------------------
# TANQUES - SETPOINTS Y CONDICIONES (HOLDING REGISTERS - Read/Write)
# -------------------------------------------------------------------------
TANQUE_1_SP = 101
TANQUE_2_SP = 102
TANQUE_3_SP = 103
TANQUE_4_SP = 104
TANQUE_5_SP = 105

TANQUE_2_CONDICION = 320
TANQUE_4_CONDICION = 340

# -------------------------------------------------------------------------
# PIDs (HOLDING REGISTERS - Read/Write)
# -------------------------------------------------------------------------
PID_T2_SP = 420
PID_T2_KP = 422
PID_T2_TI = 424
PID_T2_TD = 426

PID_T4_SP = 440
PID_T4_KP = 442
PID_T4_TI = 444
PID_T4_TD = 446

# -------------------------------------------------------------------------
# ACTUADORES ANALOGICOS (SALIDAS ANALOGICAS - Write)
# -------------------------------------------------------------------------
RESISTENCIA_T2 = 5000
RESISTENCIA_T4 = 5001
VALVULA_NEUMATICA = 206
VFD = 207
