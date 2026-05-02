# Instrumentacion-industrial
TPFinal de instrumentación. control de sistemas de tanques.

## 🛠️ Requisitos
- **Python 3.9+**
- PLC compatible con Modbus TCP (o simulador en la IP configurada).

## 📥 Instalación

1.  **Clonar el repositorio** (o descargar los archivos):
    ```bash
    git clone <url-del-repositorio>
    cd Instrumentacion-industrial
    ```

2.  **Crear y activar un entorno virtual**:
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuración
Edita el archivo `config.py` para ajustar los parámetros de tu red:
- `PLC_IP`: Dirección IP de tu PLC (ej. `192.168.1.10`).
- `PLC_PORT`: Puerto Modbus (por defecto `502`).
- `MODBUS_RETRIES`: Número de intentos de reconexión antes de entrar en modo simulación.

## 🚀 Ejecución
Para iniciar el servidor SCADA:
```bash
python app.py
```
El sistema estará disponible en `http://localhost:8080` (o `https` si tienes los certificados `server.crt`/`server.key` en la raíz).
