import random 

# =========================================================================
# FUNCIONES AUXILIARES PARA SIMULACION. Simula datos para usar sin PLC
# =========================================================================
def get_mock_status():
    """Genera datos hardcodeados para pruebas sin PLC."""
    # Simular algunas variaciones leves
    t2_temp = 25.0 + random.uniform(-0.5, 0.5)
    t4_temp = 30.0 + random.uniform(-0.5, 0.5)
    
    return {
        "coils_inputs": [True, False, True, False] + [False]*10,
        "coils_outputs": [False]*10,
        "pid_flags": {
            "t4_permiso": True, "t4_activo": False,
            "t2_permiso": True, "t2_activo": False
        },
        "registers_inputs": [
            int(t2_temp * 1000 / 75), # Temp T2
            int(t4_temp * 1000 / 75), # Temp T4
            5000, 6000, 7000, 8000 # Niveles T1-T4
        ],
        "registers_outputs": [0, 4000, 4000, 0],
        "sp_niveles": [50, 50, 50, 50, 50],
        "pid_t2": {
            'params': {'setpoint': 25.0, 'kp': 1.0, 'ti': 10.0, 'td': 0.0},
            'status': {'temp_actual': round(t2_temp, 1), 'error': 0.0, 'salida': 0.0}
        },
        "pid_t4": {
            'params': {'setpoint': 30.0, 'kp': 1.0, 'ti': 10.0, 'td': 0.0},
            'status': {'temp_actual': round(t4_temp, 1), 'error': 0.0, 'salida': 0.0}
        },
        "simulated": True
    }
