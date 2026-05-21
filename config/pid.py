from models.iot_models import PID
from . import addresses
from .virtual_buttons import BTN_PID_T2, BTN_PID_T4

# NOTA
# HOLDING REGISTER %MW

PID_T2 : PID = PID(
    nombre= 'PID TANQUE 2',
    identifier = 1,
    set_point=1,
    address_set_point=addresses.PID_T2_SP,
    kp=1,
    address_kp=addresses.PID_T2_KP,
    ti=1,
    address_ti=addresses.PID_T2_TI,
    td=1,
    address_td=addresses.PID_T2_TD,
    boton_virtual_address=BTN_PID_T2.address
)

PID_T4 : PID = PID(
    nombre= 'PID TANQUE 4',
    identifier = 2,
    set_point=1,
    address_set_point=addresses.PID_T4_SP,
    kp=1,
    address_kp=addresses.PID_T4_KP,
    ti=1,
    address_ti=addresses.PID_T4_TI,
    td=1,
    address_td=addresses.PID_T4_TD,
    boton_virtual_address=BTN_PID_T4.address
)