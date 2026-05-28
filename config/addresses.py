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
BTN_PID_LAB = 344

# -------------------------------------------------------------------------
# ENTRADAS DIGITALES MONITOREADAS (COILS - Read)
# (Botones físicos copiados a %M por el PLC)
# -------------------------------------------------------------------------
BOTON_EV_1 = 101
BOTON_EV_2 = 102
BOTON_EV_3 = 103
BOTON_EV_4 = 104
BOTON_EV_5 = 105
BOTON_EV_6 = 106
BOTON_EV_7 = 107
BOTON_EV_8 = 108

LLAVE_MANDO_REMOTO = 114
BOTON_VN = 113

# -------------------------------------------------------------------------
# ELECTRO VALVULAS - SALIDAS DIGITALES (COILS - Write)
# -------------------------------------------------------------------------
ELECTRO_VALVULA_1 = 121
ELECTRO_VALVULA_2 = 122
ELECTRO_VALVULA_3 = 123
ELECTRO_VALVULA_4 = 124
ELECTRO_VALVULA_5 = 125
ELECTRO_VALVULA_6 = 126
ELECTRO_VALVULA_7 = 127
ELECTRO_VALVULA_8 = 128

# -------------------------------------------------------------------------
# TANQUES - CONDICIONES DE NIVEL (COILS - Read)
# -------------------------------------------------------------------------
TANQUE_2_CONDICION = 320
TANQUE_4_CONDICION = 340

# -------------------------------------------------------------------------
# SENSORES (INPUT REGISTERS - Read)
# -------------------------------------------------------------------------
SENSOR_PRESION_T1 = 10
SENSOR_PRESION_T2 = 20
SENSOR_PRESION_T3 = 30
SENSOR_PRESION_T4= 40

SENSOR_TEMP_T2 = 232
SENSOR_TEMP_T4 = 234

# -------------------------------------------------------------------------
# TANQUES - SETPOINTS (HOLDING REGISTERS - Read/Write)
# -------------------------------------------------------------------------
TANQUE_1_SP = 101
TANQUE_2_SP = 102
TANQUE_3_SP = 103
TANQUE_4_SP = 104
TANQUE_5_SP = 105

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

PID_LAB_SP = 460
PID_LAB_KP = 462
PID_LAB_TI = 464
PID_LAB_TD = 466

# -------------------------------------------------------------------------
# ACTUADORES ANALOGICOS (SALIDAS ANALOGICAS - Write)
# -------------------------------------------------------------------------
RESISTENCIA_T2 = 222
RESISTENCIA_T4 = 224
VALVULA_NEUMATICA = 206
VFD = 207
