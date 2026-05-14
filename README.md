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

## 🔐 Gestión de Contraseñas (Raspberry Pi)

### ¿Cómo cambiar la contraseña de la Raspberry?
No necesitas formatear ni reinstalar nada. Solo sigue estos pasos:
1. Conéctate a tu Raspberry desde una terminal:
   ```bash
   ssh admin@plc-server.local
   ```
2. Ejecuta el comando de cambio de contraseña:
   ```bash
   passwd
   ```
3. Ingresa tu contraseña actual, y luego la nueva dos veces. *(Nota: Por seguridad en Linux, al teclear no verás que se escriben asteriscos, pero el sistema sí lo está registrando).*

### ¿Cómo recibir un aviso automático (Telegram) al cambiar la clave?

> [!WARNING]
> **REQUISITO DE INTERNET:** Telegram funciona estrictamente a través de Internet. Si al desconectar el PLC y conectar tu PC por Ethernet la Raspberry se queda totalmente aislada de la red exterior (sin Wi-Fi configurado), el aviso fallará porque no podrá conectarse a los servidores de Telegram. Asegúrate de que la Raspberry tenga conexión a Internet (por ejemplo, vía Wi-Fi) para que los avisos y el bot funcionen en paralelo a la red local Ethernet.

Para evitar perder la nueva clave, puedes configurar tu Raspberry Pi para que dispare un aviso usando PAM.

**Script rápido (Listo para copiar y pegar):**
Copia el siguiente bloque de código tal cual está, pégalo en la terminal de tu Raspberry Pi y presiona Enter. ¡Ya contiene tus credenciales personales!

```bash
# 1. Crear el script de alerta
cat << 'EOF' | sudo tee /usr/local/bin/alerta_clave.sh > /dev/null
#!/bin/bash
if [ "$PAM_TYPE" = "password" ]; then
    TOKEN="8439612567:AAGX6hBDJov2PuyeljEMULHSATNvsCYpLoM"
    CHAT_ID="8562283985"
    
    curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d chat_id=${CHAT_ID} \
    -d text="⚠️ ALERTA: La contraseña de acceso (SSH) de la Raspberry ha sido modificada por el usuario $PAM_USER." > /dev/null
fi
EOF

# 2. Darle permisos de ejecución
sudo chmod +x /usr/local/bin/alerta_clave.sh

# 3. Registrar el aviso en la seguridad del sistema
grep -q "alerta_clave.sh" /etc/pam.d/common-password || echo "password optional pam_exec.so /usr/local/bin/alerta_clave.sh" | sudo tee -a /etc/pam.d/common-password > /dev/null

echo "✅ Aviso automático configurado con éxito."
```

¡Listo! Cada vez que ejecutes `passwd` y cambies la clave, recibirás un mensaje de Telegram.

---

### Explicación Genérica (Para configurar en otros equipos)
Si necesitas replicar esto manualmente o en otro equipo con credenciales distintas, estos son los pasos técnicos que hace el script de arriba:

1. **Crear el archivo del script:**
   Abres el editor en la ruta de binarios locales:
   ```bash
   sudo nano /usr/local/bin/alerta_clave.sh
   ```
2. **Escribir el código:**
   Dentro pegas el código Bash usando tu `TU_TOKEN` y `TU_CHAT_ID`. (El `PAM_TYPE` y `PAM_USER` son variables mágicas que inyecta Linux).
3. **Dar Permisos:**
   Haces que el script sea un ejecutable válido:
   ```bash
   sudo chmod +x /usr/local/bin/alerta_clave.sh
   ```
4. **Vincularlo a PAM (Pluggable Authentication Modules):**
   Abres la configuración central de contraseñas de Linux:
   ```bash
   sudo nano /etc/pam.d/common-password
   ```
   Y le indicas al sistema que, al final del proceso de cambio de clave, llame a tu script de forma opcional añadiendo esta línea al final del archivo:
   `password optional pam_exec.so /usr/local/bin/alerta_clave.sh`

---
*Desarrollado para la materia de Instrumentación Industrial.*
