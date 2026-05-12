# 🏭 Sistema de Control de Tanques (SCADA)

Este proyecto es una interfaz para monitorear y controlar tanques industriales a través de una computadora o un celular (vía Telegram). Está diseñado para funcionar en una Raspberry Pi conectada a un PLC.

---

## 🚀 Guía Rápida para Usuarios

### 1. ¿Cómo poner en marcha el sistema?
Si quieres probar el sistema en tu propia computadora:
1. **Abre una terminal** (o símbolo del sistema) en la carpeta del proyecto.
2. **Escribe este comando** y presiona Enter:
   ```
   python app.py
   ```
3. **Abre tu navegador** y escribe: `http://localhost:8080`
   *Aquí verás los tanques, niveles y podrás controlar las válvulas.*

---

### 2. ¿Cómo enviar cambios a la Raspberry Pi?
Si has modificado algo y quieres que se actualice en el equipo real (Raspberry Pi):
1. Asegúrate de que la Raspberry esté encendida y conectada a la red.
2. Busca el archivo llamado **`deploy.bat`** en la carpeta principal.
3. Haz **doble clic** en él.
4. Se abrirá una ventana negra que enviará automáticamente todos los archivos nuevos, instalará lo necesario y reiniciará el sistema.
5. Al terminar, presiona cualquier tecla para cerrar la ventana.

---

### 3. ¿Cómo cambiar la configuración (sin saber programar)?
Casi todo lo que puedes personalizar está dentro de la carpeta llamada `config`. No necesitas tocar el código principal, solo estos archivos:

*   **¿Cambiar la IP del PLC?**: Abre `config/plc.py` y cambia el número en `PLC_IP`.
*   **¿Configurar el Bot de Telegram?**: Abre `config/telegram_cfg.py` y pega tu token.
*   **¿Cambiar niveles críticos o nombres?**: Revisa los archivos `config/tanks.py` o `config/sensors.py`.

*Nota: Después de cambiar cualquier archivo de configuración, debes ejecutar el **deploy.bat** para que los cambios surtan efecto en la Raspberry Pi.*

---

### 4. Uso del Bot de Telegram 🤖
El sistema tiene un bot que te avisa el estado del servidor.
- Busca tu bot en Telegram.
- Escribe `/start` para ver las opciones.
- Escribe `/link` para obtener la dirección web actual (muy útil si la IP de la Raspberry cambia).
- Escribe `/status` para saber si el sistema está encendido y funcionando.

---

## 🛠️ Notas para la Instalación Inicial
Si es la primera vez que usas este proyecto en una computadora nueva:
1. Instala **Python 3.9** o superior.
2. Instala las librerías necesarias con este comando:
   ```
   pip install -r requirements.txt
   ```

---
*Desarrollado para la materia de Instrumentación Industrial.*
