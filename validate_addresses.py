#!/usr/bin/env python3
"""
Script de Validación de Direcciones Modbus
Detecta conflictos, espacios sin usar y valida la integridad del mapeo
"""

import sys
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Importar configuraciones
sys.path.insert(0, '.')

try:
    from config.plc import PLC_IP, PLC_PORT
    from config.sensors import (
        SENSOR_PRESION_T1, SENSOR_PRESION_T2, SENSOR_PRESION_T3,
        SENSOR_PRESION_T4, SENSOR_TEMP_T2, SENSOR_TEMP_T4
    )
    from config.valves import (
        ELECTRO_VALVULA_1, ELECTRO_VALVULA_2, ELECTRO_VALVULA_3,
        ELECTRO_VALVULA_4, ELECTRO_VALVULA_5, ELECTRO_VALVULA_6,
        ELECTRO_VALVULA_7, ELECTRO_VALVULA_8
    )
    from config.virtual_buttons import (
        BTN_GRUPO_A, BTN_GRUPO_B,
        BTN_VALVULA_1, BTN_VALVULA_2, BTN_VALVULA_3, BTN_VALVULA_4,
        BTN_VALVULA_5, BTN_VALVULA_6, BTN_VALVULA_7, BTN_VALVULA_8,
        BTN_PID_T2, BTN_PID_T4,
        BOTON_EV_1, BOTON_EV_2, BOTON_EV_3, BOTON_EV_4,
        BOTON_EV_5, BOTON_EV_6, BOTON_EV_7, BOTON_EV_8,
        LLAVE_MANDO_REMOTO
    )
    from config.tanks import TANQUE_1, TANQUE_2, TANQUE_3, TANQUE_4, TANQUE_5
    from config.pid import PID_T2, PID_T4
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)


class ModbusAddressValidator:
    """Valida la integridad y consistencia del mapeo de direcciones Modbus"""
    
    def __init__(self):
        self.coils: Dict[int, str] = {}
        self.discrete_inputs: Dict[int, str] = {}  # %I - Entradas digitales del hardware
        self.input_registers: Dict[int, str] = {}
        self.holding_registers: Dict[int, str] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def register_coil(self, address: int, name: str, obj_type: str = ""):
        """Registra un coil, detectando conflictos"""
        if address in self.coils:
            self.errors.append(
                f"⚠️ CONFLICTO DE COIL {address}: '{self.coils[address]}' vs '{name}' ({obj_type})"
            )
        else:
            self.coils[address] = f"{name} ({obj_type})"
    
    def register_discrete_input(self, address: int, name: str, obj_type: str = ""):
        """Registra un discrete input (%I del PLC)"""
        if address in self.discrete_inputs:
            self.errors.append(
                f"⚠️ CONFLICTO DISCRETE_INPUT %I{address}: '{self.discrete_inputs[address]}' vs '{name}' ({obj_type})"
            )
        else:
            self.discrete_inputs[address] = f"{name} ({obj_type})"
    
    def register_input_register(self, address: int, name: str, obj_type: str = ""):
        """Registra un input register"""
        if address in self.input_registers:
            self.errors.append(
                f"⚠️ CONFLICTO INPUT_REG {address}: '{self.input_registers[address]}' vs '{name}' ({obj_type})"
            )
        else:
            self.input_registers[address] = f"{name} ({obj_type})"
    
    def register_holding_register(self, address: int, name: str, obj_type: str = ""):
        """Registra un holding register"""
        if address in self.holding_registers:
            self.errors.append(
                f"⚠️ CONFLICTO HOLDING_REG {address}: '{self.holding_registers[address]}' vs '{name}' ({obj_type})"
            )
        else:
            self.holding_registers[address] = f"{name} ({obj_type})"
    
    def extract_addresses(self):
        """Extrae todas las direcciones de la configuración"""
        
        print("📍 Extrayendo direcciones de SENSORES...")
        self.register_input_register(SENSOR_PRESION_T1.address, "SENSOR_PRESION_T1", "Sensor")
        self.register_input_register(SENSOR_PRESION_T2.address, "SENSOR_PRESION_T2", "Sensor")
        self.register_input_register(SENSOR_PRESION_T3.address, "SENSOR_PRESION_T3", "Sensor")
        self.register_input_register(SENSOR_PRESION_T4.address, "SENSOR_PRESION_T4", "Sensor")
        self.register_input_register(SENSOR_TEMP_T2.address, "SENSOR_TEMP_T2", "Sensor")
        self.register_input_register(SENSOR_TEMP_T4.address, "SENSOR_TEMP_T4", "Sensor")
        
        print("📍 Extrayendo direcciones de VÁLVULAS...")
        self.register_coil(ELECTRO_VALVULA_1.address, "ELECTRO_VALVULA_1", "Válvula")
        self.register_coil(ELECTRO_VALVULA_2.address, "ELECTRO_VALVULA_2", "Válvula")
        self.register_coil(ELECTRO_VALVULA_3.address, "ELECTRO_VALVULA_3", "Válvula")
        self.register_coil(ELECTRO_VALVULA_4.address, "ELECTRO_VALVULA_4", "Válvula")
        self.register_coil(ELECTRO_VALVULA_5.address, "ELECTRO_VALVULA_5", "Válvula")
        self.register_coil(ELECTRO_VALVULA_6.address, "ELECTRO_VALVULA_6", "Válvula")
        self.register_coil(ELECTRO_VALVULA_7.address, "ELECTRO_VALVULA_7", "Válvula")
        self.register_coil(ELECTRO_VALVULA_8.address, "ELECTRO_VALVULA_8", "Válvula")
        
        print("📍 Extrayendo direcciones de BOTONES VIRTUALES Y ENTRADAS...")
        # Botones virtuales (COILS %M) - Comandos desde SCADA -> PLC
        self.register_coil(BTN_GRUPO_A.address, "BTN_GRUPO_A", "Botón Virtual")
        self.register_coil(BTN_GRUPO_B.address, "BTN_GRUPO_B", "Botón Virtual")
        self.register_coil(BTN_VALVULA_1.address, "BTN_VALVULA_1", "Botón Virtual")
        self.register_coil(BTN_VALVULA_2.address, "BTN_VALVULA_2", "Botón Virtual")
        self.register_coil(BTN_VALVULA_3.address, "BTN_VALVULA_3", "Botón Virtual")
        self.register_coil(BTN_VALVULA_4.address, "BTN_VALVULA_4", "Botón Virtual")
        self.register_coil(BTN_VALVULA_5.address, "BTN_VALVULA_5", "Botón Virtual")
        self.register_coil(BTN_VALVULA_6.address, "BTN_VALVULA_6", "Botón Virtual")
        self.register_coil(BTN_VALVULA_7.address, "BTN_VALVULA_7", "Botón Virtual")
        self.register_coil(BTN_VALVULA_8.address, "BTN_VALVULA_8", "Botón Virtual")
        self.register_coil(BTN_PID_T2.address, "BTN_PID_T2", "Botón Virtual")
        self.register_coil(BTN_PID_T4.address, "BTN_PID_T4", "Botón Virtual")
        
        # Entradas digitales monitoreadas (COILS %M 30-38) - Copia de %I del PLC
        self.register_coil(BOTON_EV_1.address, "BOTON_EV_1", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_2.address, "BOTON_EV_2", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_3.address, "BOTON_EV_3", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_4.address, "BOTON_EV_4", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_5.address, "BOTON_EV_5", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_6.address, "BOTON_EV_6", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_7.address, "BOTON_EV_7", "Entrada Monitoreada")
        self.register_coil(BOTON_EV_8.address, "BOTON_EV_8", "Entrada Monitoreada")
        self.register_coil(LLAVE_MANDO_REMOTO.address, "LLAVE_MANDO_REMOTO", "Entrada Monitoreada")
        
        print("📍 Extrayendo direcciones de TANQUES...")
        self.register_holding_register(TANQUE_1.SetPoint_Level, "TANQUE_1::SetPoint_Level", "Tanque")
        self.register_holding_register(TANQUE_2.SetPoint_Level, "TANQUE_2::SetPoint_Level", "Tanque")
        self.register_coil(TANQUE_2.condicion_de_nivel, "TANQUE_2::condicion_de_nivel", "Condición de Nivel")
        self.register_holding_register(TANQUE_3.SetPoint_Level, "TANQUE_3::SetPoint_Level", "Tanque")
        self.register_holding_register(TANQUE_4.SetPoint_Level, "TANQUE_4::SetPoint_Level", "Tanque")
        self.register_coil(TANQUE_4.condicion_de_nivel, "TANQUE_4::condicion_de_nivel", "Condición de Nivel")
        self.register_holding_register(TANQUE_5.SetPoint_Level, "TANQUE_5::SetPoint_Level", "Tanque")
        
        print("📍 Extrayendo direcciones de PIDs...")
        self.register_holding_register(PID_T2.address_set_point, "PID_T2::SetPoint", "PID")
        self.register_holding_register(PID_T2.address_kp, "PID_T2::Kp", "PID")
        self.register_holding_register(PID_T2.address_ti, "PID_T2::Ti", "PID")
        self.register_holding_register(PID_T2.address_td, "PID_T2::Td", "PID")
        
        self.register_holding_register(PID_T4.address_set_point, "PID_T4::SetPoint", "PID")
        self.register_holding_register(PID_T4.address_kp, "PID_T4::Kp", "PID")
        self.register_holding_register(PID_T4.address_ti, "PID_T4::Ti", "PID")
        self.register_holding_register(PID_T4.address_td, "PID_T4::Td", "PID")
    
    def validate(self):
        """Ejecuta todas las validaciones"""
        
        print("\n" + "="*70)
        print("🔍 VALIDADOR DE DIRECCIONES MODBUS")
        print("="*70 + "\n")
        
        self.extract_addresses()
        
        # Validar rangos
        print("\n📊 VALIDANDO RANGOS...")
        self._validate_ranges()
        
        # Buscar huecos
        print("\n🔎 ANALIZANDO HUECOS...")
        self._find_gaps()
        
        # Validar configuración
        print("\n✓ VALIDANDO CONFIGURACIÓN...")
        self._validate_configuration()
    
    def _validate_ranges(self):
        """Valida que las direcciones estén dentro de rangos válidos"""
        for addr in self.coils:
            if not (0 <= addr <= 9999):
                self.errors.append(f"❌ COIL {addr} fuera de rango válido (0-9999)")
        
        for addr in self.discrete_inputs:
            if not (0 <= addr <= 9999):
                self.errors.append(f"❌ DISCRETE_INPUT %I{addr} fuera de rango válido (0-9999)")
        
        for addr in self.input_registers:
            if not (0 <= addr <= 9999):
                self.errors.append(f"❌ INPUT_REG {addr} fuera de rango válido (0-9999)")
        
        for addr in self.holding_registers:
            if not (0 <= addr <= 9999):
                self.errors.append(f"❌ HOLDING_REG {addr} fuera de rango válido (0-9999)")
    
    def _find_gaps(self):
        """Identifica espacios sin usar para optimización futura"""
        def analyze_gaps(addresses: Dict[int, str], addr_type: str):
            if not addresses:
                return
            
            sorted_addrs = sorted(addresses.keys())
            gaps = []
            
            for i in range(len(sorted_addrs) - 1):
                current = sorted_addrs[i]
                next_addr = sorted_addrs[i + 1]
                if next_addr - current > 1:
                    gap_size = next_addr - current - 1
                    gaps.append((current, next_addr, gap_size))
            
            if gaps:
                print(f"\n  📌 {addr_type}:")
                for start, end, size in gaps:
                    print(f"     Brecha: {start}..{end} ({size} direcciones disponibles)")
            
            # Espacio antes del primer
            if sorted_addrs[0] > 0:
                print(f"\n  📌 {addr_type}: {sorted_addrs[0]} direcciones disponibles antes de {sorted_addrs[0]}")
        
        analyze_gaps(self.coils, "COILS (%M)")
        analyze_gaps(self.discrete_inputs, "DISCRETE INPUTS (%I)")
        analyze_gaps(self.input_registers, "INPUT REGISTERS (%IW)")
        analyze_gaps(self.holding_registers, "HOLDING REGISTERS (%MW)")
    
    def _validate_configuration(self):
        """Valida la configuración de conexión"""
        print(f"  ✓ IP del PLC: {PLC_IP}")
        print(f"  ✓ Puerto Modbus: {PLC_PORT}")
        
        if PLC_PORT != 502:
            self.warnings.append(f"⚠️ Puerto Modbus inusual ({PLC_PORT}), se esperaba 502")
    
    def print_report(self):
        """Imprime el reporte final"""
        print("\n" + "="*70)
        print("📋 REPORTE DE VALIDACIÓN")
        print("="*70)
        
        # Estadísticas
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  • Coils utilizados (%M): {len(self.coils)}")
        print(f"  • Discrete Inputs utilizados (%I): {len(self.discrete_inputs)}")
        print(f"  • Input Registers utilizados (%IW): {len(self.input_registers)}")
        print(f"  • Holding Registers utilizados (%MW): {len(self.holding_registers)}")
        print(f"  • Total direcciones: {len(self.coils) + len(self.discrete_inputs) + len(self.input_registers) + len(self.holding_registers)}")
        
        # Detalles
        if self.coils:
            print(f"\n🔴 COILS / MEMORY (%M) ({len(self.coils)}):")
            for addr in sorted(self.coils.keys()):
                print(f"  %M{addr:3d}: {self.coils[addr]}")
        
        if self.discrete_inputs:
            print(f"\n🟣 DISCRETE INPUTS (%I) ({len(self.discrete_inputs)}):")
            for addr in sorted(self.discrete_inputs.keys()):
                print(f"  %I{addr:3d}: {self.discrete_inputs[addr]}")
        
        if self.input_registers:
            print(f"\n🔵 INPUT REGISTERS (%IW) ({len(self.input_registers)}):")
            for addr in sorted(self.input_registers.keys()):
                print(f"  %IW{addr:3d}: {self.input_registers[addr]}")
        
        if self.holding_registers:
            print(f"\n🟡 HOLDING REGISTERS (%MW) ({len(self.holding_registers)}):")
            for addr in sorted(self.holding_registers.keys()):
                print(f"  %MW{addr:3d}: {self.holding_registers[addr]}")
        
        # Errores y warnings
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ VALIDACIÓN EXITOSA: No hay conflictos detectados")
        
        print("\n" + "="*70 + "\n")
        
        # Retornar código de salida
        return 0 if not self.errors else 1


def main():
    validator = ModbusAddressValidator()
    validator.validate()
    exit_code = validator.print_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
