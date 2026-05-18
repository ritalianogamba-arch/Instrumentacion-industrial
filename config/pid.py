from models.iot_models import PID
from .virtual_buttons import BTN_PID_T2, BTN_PID_T4

# NOTA
# HOLDING REGISTER %MW

PID_T2 : PID = PID(
    nombre= 'PID TANQUE 2',
    identifier = 1,
    set_point=1,
    address_set_point=420,
    kp=1,
    address_kp=422,
    ti=1,
    address_ti=424,
    td=1,
    address_td=426,
    boton_virtual_address=BTN_PID_T2.address
)

PID_T4 : PID = PID(
    nombre= 'PID TANQUE 4',
    identifier = 2,
    set_point=1,
    address_set_point=440,
    kp=1,
    address_kp=442,
    ti=1,
    address_ti=444,
    td=1,
    address_td=446,
    boton_virtual_address=BTN_PID_T4.address
)