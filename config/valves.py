from models.iot_models import SalidaDigital
from .buttons import (
    BOTON_EV_1, BOTON_EV_2, BOTON_EV_3, BOTON_EV_4,
    BOTON_EV_5, BOTON_EV_6, BOTON_EV_7, BOTON_EV_8
)

# =========================================================================
# ELECTRO VALVULAS
# =========================================================================

# NOTA:
# Addres = %M (USAR READ/WRITE COIL)
# Digital = %I
# Server = %M

ELECTRO_VALVULA_1 = SalidaDigital(
    address=100, 
    estado=None,
    entrada_digital=BOTON_EV_1.address,
    entrada_server=14,
)

ELECTRO_VALVULA_2 = SalidaDigital(
    address=101, 
    estado=None,
    entrada_digital=BOTON_EV_2.address,
    entrada_server=15,
)

ELECTRO_VALVULA_3 = SalidaDigital(
    address=102, 
    estado=None,
    entrada_digital=BOTON_EV_3.address,
    entrada_server=16,
)

ELECTRO_VALVULA_4 = SalidaDigital(
    address=103, 
    estado=None,
    entrada_digital=BOTON_EV_4.address,
    entrada_server=17,
)

ELECTRO_VALVULA_5 = SalidaDigital(
    address=104, 
    estado=None,
    entrada_digital=BOTON_EV_5.address,
    entrada_server=18,
)

ELECTRO_VALVULA_6 = SalidaDigital(
    address=105, 
    estado=None,
    entrada_digital=BOTON_EV_6.address,
    entrada_server=19,
)

ELECTRO_VALVULA_7 = SalidaDigital(
    address=106, 
    estado=None,
    entrada_digital=BOTON_EV_7.address,
    entrada_server=20,
)

ELECTRO_VALVULA_8 = SalidaDigital(
    address=107, 
    estado=None,
    entrada_digital=BOTON_EV_8.address,
    entrada_server=21,
)
