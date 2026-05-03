from models.iot_models import PID

# NOTA
# HOLDING REGISTER %MW

PID_T2 : PID = PID(
    nombre= 'PID TANQUE 2',
    identifier = 1,
    set_point=1,
    address_set_point=400,
    kp=1,
    address_kp=402,
    ti=1,
    address_ti=404,
    td=1,
    address_td=406,
)

PID_T4 : PID = PID(
    nombre= 'PID TANQUE 4',
    identifier = 2,
    set_point=1,
    address_set_point=420,
    kp=1,
    address_kp=422,
    ti=1,
    address_ti=424,
    td=1,
    address_td=426,
)