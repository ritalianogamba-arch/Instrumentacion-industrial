from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EntradaDigital:
    """
    Representa una entrada digital (contacto físico).
    """
    nombre: str
    address: int
    estado: bool = False
    salida: Optional[int] = None  # Ligado a una salida de manera opcional

@dataclass
class EntradaAnalogica:
    """
    Representa una entrada analógica (sensor).
    """
    nombre: str
    address: int
    estado: float = 0.0
    salida: Optional[int] = None  # Ligado a una salida de manera opcional

@dataclass
class SalidaDigital:
    """
    Representa una salida digital ligada a diferentes tipos de entradas.
    """
    nombre: str
    address: int
    identificador: int = 0  # Identificador visual (1, 2, 3...)
    estado: bool = False
    entrada_digital: Optional[int] = None       # Botón Fisico (Address)
    entrada_analogica: Optional[int] = None     # Entrada tipo sensor (Address)
    entrada_server: Optional[int] = None        # Servidor boton pagina(Address)

@dataclass
class SalidaAnalogica:
    """
    Representa una salida analógica.
    """
    nombre: str
    address: int
    estado: float = 0.0

@dataclass
class BotonVirtual:
    """
    Representa un botón en la interfaz del SCADA que envía comandos al PLC.
    """
    nombre: str
    address: int
    descripcion: Optional[str] = None

@dataclass
class Tanque:
    """
    Representa un tanque con sus sensores y válvulas.
    """
    nombre: str
    sensor_de_presion: int  #(Address)
    valvula_superior: int   #(Address)
    valvula_inferior: int   #(Address)
    SetPoint_Level: int   #(Address)
    modo_auto_address: int  #(Address para toggle Manual/Auto)
    boton_virtual_address: int  # Dirección del botón virtual
    valvula_superior_identificador: int = 0 # ID Visual (1, 2, 3...)
    valvula_inferior_identificador: int = 0 # ID Visual (1, 2, 3...)
    sensor_de_temperatura: Optional[int] = None
    condicion_de_nivel: Optional[int] = None
    resistencia: Optional[int] = None 
    pid_id: Optional[int] = None
    # Dimensiones físicas
    altura: float = 2.0
    diametro: float = 1.0
    volumen: float = 1.5
    material: str = "Acero Inox"
    lado_controles: str = "izq" # "izq" o "der"
    lado_termometro: str = "der" # "izq" o "der"

@dataclass
class PID:
    """
    Representa un controlador PID con sus parámetros y direcciones Modbus.
    """
    nombre: str
    identifier: int
    set_point: float
    address_set_point: int
    kp: float
    address_kp: int
    ti: float
    address_ti: int
    td: float
    address_td: int
    boton_virtual_address: int  # Dirección del botón virtual
