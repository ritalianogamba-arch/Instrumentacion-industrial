# 🏗️ Arquitectura del Sistema SCADA

## 📚 Índice de Documentación
- [MODBUS_MAPPING.md](MODBUS_MAPPING.md) - Mapeo completo de direcciones Modbus
- [config_modbus.json](config_modbus.json) - Configuración centralizada en JSON
- [validate_addresses.py](validate_addresses.py) - Script para validar integridad de direcciones
- [README.md](README.md) - Guía de ejecución

---

## 🔗 Componentes Principales

### 1. **Capa de Conexión Modbus** (`modbus_core.py`)
```
┌─────────────────────────────────────────┐
│     ModbusClientManager                 │
│  Gestiona conexión TCP/IP con PLC       │
│  - Reconexión automática                │
│  - Thread safety con locks              │
│  - Cooldown de reconexiones             │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ PLC 192.168.1.10 │
        │ Port 502         │
        └──────────────────┘
```

**Configuración**:
- `IP`: 192.168.1.10 (en `config/plc.py`)
- `Puerto`: 502 (Modbus TCP estándar)
- `Timeout`: 5 segundos
- `Reintentos`: 2 intentos antes de modo simulación

---

### 2. **Capa de Configuración** (`config/`)

#### Estructura de Directorios
```
config/
├── __init__.py
├── plc.py              # Conexión PLC + escalamiento
├── flask_cfg.py        # Servidor web (0.0.0.0:8080)
├── sensors.py          # 6 sensores analógicos (presión + temperatura)
├── valves.py           # 8 electroválvulas digitales
├── virtual_buttons.py  # 12 botones virtuales de control
├── tanks.py            # 5 tanques con setpoints
├── pid.py              # 2 lazos PID (T2, T4)
├── actuator.py         # 2 resistencias térmicas
├── logging_cfg.py      # Logging centralizado
├── telegram_cfg.py     # Bot de Telegram
└── data.py             # Modelos de datos
```

---

### 3. **Mapeo de Direcciones Modbus**

#### 📊 Resumen de Utilizacion
```
┌──────────────────────────────────────────────────┐
│          ESPACIO MODBUS DISPONIBLE               │
│           (0 a 65536 direcciones)                │
├──────────────────────────────────────────────────┤
│ COILS (Digitales):                               │
│   0-8:     Botones de válvulas                   │
│   13:      Llave de control remoto               │
│   20-21:   Modos de grupo (Auto/Manual)          │
│   100-106: Electroválvulas 1-7                   │
│   321, 341: Activación de PIDs                   │
│                                                  │
│ INPUT REGISTERS (Lectura):                       │
│   201-204: Sensores de presión (T1-T5)           │
│   302, 304: Sensores de temperatura (T2, T4)     │
│                                                  │
│ HOLDING REGISTERS (Lectura/Escritura):           │
│   101-105: SetPoints de nivel (T1-T5)            │
│   320, 340: Condiciones auxiliares               │
│   420-426: Parámetros PID T2                     │
│   440-446: Parámetros PID T4                     │
└──────────────────────────────────────────────────┘
```

**Total**: 49 direcciones utilizadas (~0.07% del espacio disponible)

---

### 4. **Tanques y Lógica**

```
GRUPO A (Modo Auto: COIL 20)          GRUPO B (Modo Auto: COIL 21)
├── Tanque 1                          ├── Tanque 4 (Con PID)
│   ├── Presión: REG 201              │   ├── Presión: REG 204
│   └── SetPoint: REG 101             │   ├── Temperatura: REG 304
│                                      │   ├── SetPoint: REG 104
├── Tanque 2 (Con PID)                │   ├── Parámetros PID:
│   ├── Presión: REG 202              │   │   ├── SetPoint: REG 440
│   ├── Temperatura: REG 302          │   │   ├── Kp: REG 442
│   ├── SetPoint: REG 102             │   │   ├── Ti: REG 444
│   ├── Parámetros PID:               │   │   └── Td: REG 446
│   │   ├── SetPoint: REG 420         │   └── Activación: COIL 341
│   │   ├── Kp: REG 422               │
│   │   ├── Ti: REG 424               └── Tanque 5
│   │   └── Td: REG 426               │   ├── Presión: REG 204
│   └── Activación: COIL 321          │   └── SetPoint: REG 105
│
└── Tanque 3
    ├── Presión: REG 203
    └── SetPoint: REG 103
```

---

### 5. **Control de Válvulas**

```
ELECTROVÁLVULA (Sálida Física)         BOTÓN VIRTUAL (Control)
├── COIL 100 (EV1)  ◀──────────────┐   ├── COIL 1  (Comando)
├── COIL 101 (EV2)  ◀──────────────┼───┼── COIL 2  (Comando)
├── COIL 102 (EV3)  ◀──────────────┼───┼── COIL 3  (Comando)
├── COIL 103 (EV4)  ◀──────────────┼───┼── COIL 4  (Comando)
├── COIL 104 (EV5)  ◀──────────────┼───┼── COIL 5  (Comando)
├── COIL 105 (EV6)  ◀──────────────┼───┼── COIL 6  (Comando)
└── COIL 106 (EV7)  ◀──────────────┴───┴── COIL 7  (Comando)

ENTRADA FÍSICA (Hardware)
├── COIL 0 (BOTON_EV_1)
├── COIL 1 (BOTON_EV_2)
├── COIL 2 (BOTON_EV_3)
├── ... (hasta BOTON_EV_8)
└── COIL 13 (LLAVE_MANDO_REMOTO)
```

---

## 🔍 Herramientas de Validación

### 1. **Script de Validación** (`validate_addresses.py`)

Detecta conflictos, espacios sin usar y valida la integridad del mapeo.

**Uso**:
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar validación
python validate_addresses.py
```

**Salida**:
```
🔍 VALIDADOR DE DIRECCIONES MODBUS
============================================================================

📊 ESTADÍSTICAS:
  • Coils utilizados: 20
  • Input Registers utilizados: 6
  • Holding Registers utilizados: 23
  • Total direcciones: 49

✅ VALIDACIÓN EXITOSA: No hay conflictos detectados
```

### 2. **Archivo de Configuración** (`config_modbus.json`)

Centraliza toda la configuración en un único archivo JSON bien documentado.

**Estructura**:
- `plc.connection` - IP, puerto, timeouts
- `sensors` - Temperatura y presión
- `valves` - Electroválvulas
- `virtual_buttons` - Controles
- `tanks` - Información de tanques
- `pids` - Parámetros PID

**Uso futuro** (puede implementarse para cargar configuración dinámicamente):
```python
import json

with open('config_modbus.json') as f:
    config = json.load(f)
    
plc_ip = config['plc']['connection']['ip']
plc_port = config['plc']['connection']['port']
```

---

## 🔄 Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│  NAVEGADOR WEB / APLICACIÓN MÓVIL / BOT TELEGRAM       │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────▼─────────┐
        │  Flask Server    │ (0.0.0.0:8080)
        │  app.py          │
        └────────┬─────────┘
                 │
        ┌────────▼─────────────────┐
        │  API Routes              │ (api_routes.py)
        │  - GET /status           │
        │  - POST /control/valve   │
        │  - POST /control/setpoint│
        └────────┬─────────────────┘
                 │
        ┌────────▼──────────────────┐
        │  Supervisores            │ (supervisors.py)
        │  - supervisor_tacho_2    │
        │  - supervisor_tacho_4    │
        └────────┬──────────────────┘
                 │
        ┌────────▼────────────────────────┐
        │  Modbus Core                    │ (modbus_core.py)
        │  - ModbusClientManager          │
        │  - safe_modbus_operation()      │
        │  - read_coils_safe()            │
        │  - write_coil_safe()            │
        │  - read_registers_safe()        │
        └────────┬────────────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  Pymodbus TCP Client        │
        │  (Thread-safe, pooling)     │
        └────────┬────────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  Red TCP/IP                 │
        └────────┬────────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  PLC 192.168.1.10:502       │
        │  Controlador Modbus TCP     │
        └────────┬────────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  E/S Digitales y Analógicas │
        │  - Válvulas (COIL)          │
        │  - Sensores (REG)           │
        └─────────────────────────────┘
```

---

## 📋 Validación de Implementación

### ✅ Aspectos Correctos

1. **Thread Safety**: Uso correcto de `threading.Lock()` en modbus_core.py
2. **Escalamiento**: Fórmulas correctas para temperatura y presión
3. **Organización**: Configuración modular en archivos separados
4. **Naming**: Convenciones claras (SENSOR_*, ELECTRO_*, BTN_*)
5. **Documentación**: Comentarios descriptivos en código

### ⚠️ Consideraciones de Mejora

1. **Variables de Entorno**: IP/Puerto del PLC están hardcodeados
   - Solución: Usar `.env` o variables de entorno del sistema

2. **Validación de Tipos**: Los modelos IoT podrían usar type hints más estrictos
   - Solución: Agregar validación en `models/iot_models.py`

3. **Documentación de API**: Las rutas Flask no están totalmente documentadas
   - Solución: Agregar docstrings en `api_routes.py`

4. **Tests Unitarios**: No hay tests para validar la lógica
   - Solución: Crear carpeta `tests/` con tests de unidad

---

## 📦 Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `app.py` | Punto de entrada, inicializa Flask y hilos |
| `modbus_core.py` | Gestión de conexión Modbus con thread safety |
| `api_routes.py` | Rutas Flask para API |
| `supervisors.py` | Bucles de control para PIDs |
| `bot_telegram.py` | Bot de Telegram para notificaciones |
| `config/plc.py` | Configuración de PLC y escalamiento |
| `config/*.py` | Definición de elementos (sensores, válvulas, tanques) |
| `models/iot_models.py` | Clases base para elementos IoT |
| `templates/index.html` | Interfaz web |
| `static/js/*.js` | Lógica frontend |

---

## 🚀 Próximos Pasos Recomendados

1. **Ejecutar validación**: `python validate_addresses.py`
2. **Revisar mapeo**: Consultar `MODBUS_MAPPING.md`
3. **Migrar a variables de entorno** para IP/Puerto
4. **Implementar tests unitarios**
5. **Agregar logging más detallado** para depuración

