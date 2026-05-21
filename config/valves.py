from models.iot_models import SalidaDigital
from . import addresses
from .virtual_buttons import (
    BOTON_EV_1, BOTON_EV_2, BOTON_EV_3, BOTON_EV_4,
    BOTON_EV_5, BOTON_EV_6, BOTON_EV_7, BOTON_EV_8,
    BTN_VALVULA_1, BTN_VALVULA_2, BTN_VALVULA_3, BTN_VALVULA_4,
    BTN_VALVULA_5, BTN_VALVULA_6, BTN_VALVULA_7, BTN_VALVULA_8
)

# =========================================================================
# ELECTRO VALVULAS
# =========================================================================

# NOTA:
# Addres = %M (USAR READ/WRITE COIL)
# Digital = %I
# Server = %M

ELECTRO_VALVULA_1 = SalidaDigital(
    nombre='Electro Valvula 1',
    address=addresses.ELECTRO_VALVULA_1, 
    identificador=1,
    estado=None,
    entrada_digital=BOTON_EV_1.address,
    entrada_server=BTN_VALVULA_1.address,
)

ELECTRO_VALVULA_2 = SalidaDigital(
    nombre='Electro Valvula 2',
    address=addresses.ELECTRO_VALVULA_2, 
    identificador=2,
    estado=None,
    entrada_digital=BOTON_EV_2.address,
    entrada_server=BTN_VALVULA_2.address,
)

ELECTRO_VALVULA_3 = SalidaDigital(
    nombre='Electro Valvula 3',
    address=addresses.ELECTRO_VALVULA_3, 
    identificador=3,
    estado=None,
    entrada_digital=BOTON_EV_3.address,
    entrada_server=BTN_VALVULA_3.address,
)

ELECTRO_VALVULA_4 = SalidaDigital(
    nombre='Electro Valvula 4',
    address=addresses.ELECTRO_VALVULA_4, 
    identificador=4,
    estado=None,
    entrada_digital=BOTON_EV_4.address,
    entrada_server=BTN_VALVULA_4.address,
)

ELECTRO_VALVULA_5 = SalidaDigital(
    nombre='Electro Valvula 5',
    address=addresses.ELECTRO_VALVULA_5, 
    identificador=5,
    estado=None,
    entrada_digital=BOTON_EV_5.address,
    entrada_server=BTN_VALVULA_5.address,
)

ELECTRO_VALVULA_6 = SalidaDigital(
    nombre='Electro Valvula 6',
    address=addresses.ELECTRO_VALVULA_6, 
    identificador=6,
    estado=None,
    entrada_digital=BOTON_EV_6.address,
    entrada_server=BTN_VALVULA_6.address,
)

ELECTRO_VALVULA_7 = SalidaDigital(
    nombre='Electro Valvula 7',
    address=addresses.ELECTRO_VALVULA_7, 
    identificador=7,
    estado=None,
    entrada_digital=BOTON_EV_7.address,
    entrada_server=BTN_VALVULA_7.address,
)

ELECTRO_VALVULA_8 = SalidaDigital(
    nombre='Electro Valvula 8',
    address=addresses.ELECTRO_VALVULA_8, 
    identificador=8,
    estado=None,
    entrada_digital=BOTON_EV_8.address,
    entrada_server=BTN_VALVULA_8.address,
)
