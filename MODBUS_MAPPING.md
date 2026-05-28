# Mapeo de Direcciones Modbus - Sistema SCADA

## 📋 Resumen Ejecutivo
- **Protocolo**: Modbus TCP
- **PLC Destino**: 192.168.1.10:502
- **Timeout**: 5 segundos
- **Reintentos**: 2

---

## 🔌 Rango de Direcciones Utilizadas

| Tipo | Rango | Uso | Protocolo |
|------|-------|-----|-----------|
| **Coils** | 1-8, 20-21, 100-107, 321, 341, 344 | Salidas digitales (válvulas, botones) | Read/Write Coil |
| **Coils (Monitoreadas)** | 30-38 | Entradas digitales del hardware (%I) copiadas | Read Coil |
| **Input Registers** | 201-204, 302, 304 | Sensores analógicos | Read Input Register |
| **Holding Registers** | 101-105, 320, 340, 420-426, 440-446, 460-466 | SetPoints y parámetros | Read/Write Holding Register |

---

## 📍 Mapeo Detallado

### 🌡️ SENSORES (Input Registers - Lectura)

#### Presión
| Dirección | Nombre | Tanque | Unidad |
|-----------|--------|--------|--------|
| 201 | SENSOR_PRESION_T1 | Tanque 1 | PSI / bar |
| 202 | SENSOR_PRESION_T2 | Tanque 2 | PSI / bar |
| 203 | SENSOR_PRESION_T3 | Tanque 3 | PSI / bar |
| 204 | SENSOR_PRESION_T4_T5 | Tanques 4 y 5 | PSI / bar |

#### Temperatura
| Dirección | Nombre | Tanque | Unidad |
|-----------|--------|--------|--------|
| 302 | SENSOR_TEMP_T2 | Tanque 2 | °C (escalado) |
| 304 | SENSOR_TEMP_T4 | Tanque 4 | °C (escalado) |

**Fórmula de Escalamiento**: 
```
Si PLC_SENDS_SCALED_TEMP = False:
  °C = (raw_value × 75 / 1000) + 0.5
Si PLC_SENDS_SCALED_TEMP = True:
  °C = raw_value (ya escalado en PLC)
```

---

### 🚰 VÁLVULAS - SALIDAS DIGITALES (Coils - Write)

| Dirección | Nombre | ID | Entrada Digital | Entrada Server |
|-----------|--------|----|--------------------|-----------------|
| 100 | ELECTRO_VALVULA_1 | 1 | 0 (BOTON_EV_1) | 1 (BTN_VALVULA_1) |
| 101 | ELECTRO_VALVULA_2 | 2 | 1 (BOTON_EV_2) | 2 (BTN_VALVULA_2) |
| 102 | ELECTRO_VALVULA_3 | 3 | 2 (BOTON_EV_3) | 3 (BTN_VALVULA_3) |
| 103 | ELECTRO_VALVULA_4 | 4 | 3 (BOTON_EV_4) | 4 (BTN_VALVULA_4) |
| 104 | ELECTRO_VALVULA_5 | 5 | 4 (BOTON_EV_5) | 5 (BTN_VALVULA_5) |
| 105 | ELECTRO_VALVULA_6 | 6 | 5 (BOTON_EV_6) | 6 (BTN_VALVULA_6) |
| 106 | ELECTRO_VALVULA_7 | 7 | 6 (BOTON_EV_7) | 7 (BTN_VALVULA_7) |
| - | ELECTRO_VALVULA_8 | 8 | 7 (BOTON_EV_8) | 8 (BTN_VALVULA_8) |

---

### 🎮 CONTROLES - BOTONES VIRTUALES (Coils - Write)

#### Modos de Grupo (Manual/Auto)
| Dirección | Nombre | Grupo | Descripción |
|-----------|--------|-------|-------------|
| 20 | BTN_GRUPO_A | A | Activa modo Auto para Grupo A (T1, T2, T3) |
| 21 | BTN_GRUPO_B | B | Activa modo Auto para Grupo B (T4, T5) |

#### Comandos de Válvulas
| Dirección | Nombre | Asociado |
|-----------|--------|----------|
| 1 | BTN_VALVULA_1 | EV1 (COIL 100) |
| 2 | BTN_VALVULA_2 | EV2 (COIL 101) |
| 3 | BTN_VALVULA_3 | EV3 (COIL 102) |
| 4 | BTN_VALVULA_4 | EV4 (COIL 103) |
| 5 | BTN_VALVULA_5 | EV5 (COIL 104) |
| 6 | BTN_VALVULA_6 | EV6 (COIL 105) |
| 7 | BTN_VALVULA_7 | EV7 (COIL 106) |
| 8 | BTN_VALVULA_8 | EV8 (COIL 107) |

#### Activación de PIDs
| Dirección | Nombre | Control |
|-----------|--------|---------|
| 321 | BTN_PID_T2 | Activar PID de Tanque 2 |
| 341 | BTN_PID_T4 | Activar PID de Tanque 4 |
| 344 | BTN_PID_LAB | Activar PID Laboratorio |

#### Entradas Digitales Monitoreadas (%M 30-38)
**Nota**: El PLC debe copiar las entradas físicas (%I0.x) a estas direcciones de memoria para que el SCADA pueda monitorearlas.

| Dirección | Nombre | Hardware | Descripción |
|-----------|--------|----------|-------------|
| 30 | BOTON_EV_1 | %I0.0 | Monitor: Botón EV 1 |
| 31 | BOTON_EV_2 | %I0.1 | Monitor: Botón EV 2 |
| 32 | BOTON_EV_3 | %I0.2 | Monitor: Botón EV 3 |
| 33 | BOTON_EV_4 | %I0.3 | Monitor: Botón EV 4 |
| 34 | BOTON_EV_5 | %I0.4 | Monitor: Botón EV 5 |
| 35 | BOTON_EV_6 | %I0.5 | Monitor: Botón EV 6 |
| 36 | BOTON_EV_7 | %I0.6 | Monitor: Botón EV 7 |
| 37 | BOTON_EV_8 | %I0.7 | Monitor: Botón EV 8 |
| 13 | LLAVE_MANDO_REMOTO | %I0.13 | Monitor: Llave de Control Remoto |

---

### 🏊 TANQUES - SETPOINTS NIVEL (Holding Registers - Read/Write)

| Dirección | Tanque | Descripción | Rango | Unidad |
|-----------|--------|-------------|-------|--------|
| 101 | T1 | SetPoint Nivel Tanque 1 | 0-100 | % |
| 102 | T2 | SetPoint Nivel Tanque 2 | 0-100 | % |
| 103 | T3 | SetPoint Nivel Tanque 3 | 0-100 | % |
| 104 | T4 | SetPoint Nivel Tanque 4 | 0-100 | % |
| 105 | T5 | SetPoint Nivel Tanque 5 | 0-100 | % |

#### Condición de Nivel (Auxiliar)
| Dirección | Tanque | Descripción |
|-----------|--------|-------------|
| 320 | T2 | Nivel actual / condición (T2 + PID) |
| 340 | T4 | Nivel actual / condición (T4 + PID) |

**Nota**: Las direcciones 320 y 340 se usan para comunicación entre supervisores y lógica PLC.

---

### 🔄 PIDs - PARÁMETROS

#### PID Tanque 2 (ID: 1)
| Dirección | Parámetro | Rango | Unidad |
|-----------|-----------|-------|--------|
| 420 | SetPoint | 0-100 | °C o % |
| 422 | Kp (Proporcional) | 0-1000 | - |
| 424 | Ti (Integral) | 0-1000 | s |
| 426 | Td (Derivativa) | 0-1000 | s |

**Botón Virtual**: 321 (COIL)

#### PID Tanque 4 (ID: 2)
| Dirección | Parámetro | Rango | Unidad |
|-----------|-----------|-------|--------|
| 440 | SetPoint | 0-100 | °C o % |
| 442 | Kp (Proporcional) | 0-1000 | - |
| 444 | Ti (Integral) | 0-1000 | s |
| 446 | Td (Derivativa) | 0-1000 | s |

**Botón Virtual**: 341 (COIL)

#### PID Laboratorio (ID: 3)
| Dirección | Parámetro | Rango | Unidad |
|-----------|-----------|-------|--------|
| 460 | SetPoint | 0-100 | °C o % |
| 462 | Kp (Proporcional) | 0-1000 | - |
| 464 | Ti (Integral) | 0-1000 | s |
| 466 | Td (Derivativa) | 0-1000 | s |

**Botón Virtual**: 344 (COIL)

---

## ⚠️ Análisis de Conflictos

### ✅ Estado Actual
- **No hay overlaps** detectados entre direcciones
- Coils (0-8, 13, 20-21, 100-106, 321, 341, 344): Espaciadas correctamente
- Registers (201-204, 302, 304, 101-105, 320, 340, 420-426, 440-446, 460-466): Sin conflictos

### ✅ Organización Lógica
```
Coils 0-8:      Botones virtuales básicos (válvulas)
Coils 13:       Control remoto (llave)
Coils 20-21:    Modos de grupo
Coils 100-106:  Válvulas electromecánicas
Coils 321+:     Controles especiales (PIDs)

Registers 101-105:    SetPoints de nivel
Registers 201-204:    Sensores de presión
Registers 302-304:    Sensores de temperatura
Registers 320-340:    Condiciones auxiliares
Registers 420-466:    Parámetros PID
```

---

## 📊 Estadísticas

| Métrica | Cantidad |
|---------|----------|
| Coils Utilizados (Comandos) | 13 |
| Coils Monitoreados (Entradas) | 9 |
| Input Registers Utilizados | 6 |
| Holding Registers Utilizados | 23 |
| **Total Direcciones** | **51** |
| % de espacio usado (0-1000) | 5.1% |

---

## 🔧 Cómo Usar Este Documento

1. **Para agregar nuevos sensores**: Usar direcciones libres en 200s-300s
2. **Para agregar nuevas válvulas**: Usar direcciones libres en 100-119
3. **Para agregar nuevos PIDs**: Usar rangos similares (420+, 440+)
4. **Mantener actualizado**: Cada cambio en archivos de config debe reflejarse aquí

---

## 📝 Referencias
- `config/plc.py` - Configuración de conexión
- `config/sensors.py` - Definición de sensores
- `config/valves.py` - Definición de válvulas
- `config/virtual_buttons.py` - Botones de control
- `config/pid.py` - Parámetros PID
- `config/tanks.py` - Tanques y setpoints

