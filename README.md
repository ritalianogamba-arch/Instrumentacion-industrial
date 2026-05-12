# 🏭 Sistema de Control de Tanques (SCADA)

Este proyecto es una interfaz para monitorear y controlar tanques industriales a través de una computadora o un celular (vía Telegram). Está diseñado para funcionar en una Raspberry Pi conectada a un PLC.

---

## 🚀 Guía de Ejecución

### 1. Primera vez (Configuración inicial)
Si es la primera vez que descargas el proyecto, sigue estos pasos para configurar tu entorno:

1. **Abre una terminal** en la carpeta del proyecto.
2. **Crea un entorno virtual** (para mantener las librerías organizadas):
   ```bash
   python -m venv .venv
   ```
3. **Activa el entorno virtual**:
   - En Windows: `.venv\Scripts\activate`
   - En Linux/Mac: `source .venv/bin/activate`
4. **Instala las librerías necesarias**:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Ejecuciones posteriores
Una vez configurado, cada vez que quieras iniciar el sistema:

1. **Abre una terminal** en la carpeta del proyecto.
2. **Activa el entorno** (si no está activo): `.venv\Scripts\activate`
3. **Inicia el servidor**:
   ```bash
   python app.py
   ```
4. **Accede desde tu navegador**: `http://localhost:8080`

---

## 💎 Características Principales
- **Monitoreo en Tiempo Real**: Visualización dinámica de niveles y temperaturas.
- **Control Detallado**: Haz **doble clic** sobre cualquier tanque para abrir una ventana emergente con:
  - Dimensiones físicas detalladas (altura, diámetro, material).
  - Volumen actual calculado en tiempo real.
  - Estado de las válvulas de entrada/salida.
- **Control PID**: Gestión de temperatura mediante lazos de control configurables.
- **Bot de Telegram**: Notificaciones de estado y acceso remoto vía `/status`, `/link` y `/start`.

---

## 🛰️ Despliegue a la Raspberry Pi
Si has modificado el código y quieres actualizar la Raspberry Pi real:
1. Busca el archivo **`deploy.bat`** en la carpeta principal.
2. Haz **doble clic** en él. Este script se encarga de:
   - Sincronizar los archivos.
   - Instalar nuevas dependencias en el servidor remoto.
   - Reiniciar el servicio SCADA automáticamente.

---

## 🛠️ Configuración Personalizada
No necesitas tocar el código principal. Casi todo se ajusta en la carpeta `config`:
- **PLC**: `config/plc.py` (Cambiar `PLC_IP`).
- **Telegram**: `config/telegram_cfg.py` (Token del bot).
- **Tanques**: `config/tanks.py` (Nombres, dimensiones físicas y direcciones Modbus).

---
*Desarrollado para la materia de Instrumentación Industrial.*
