#!/bin/bash
# ============================================================
# Script de configuración automática de red para la Raspberry Pi
# Ejecutar con: sudo bash setup_red.sh
# ============================================================
#
# ╔══════════════════════════════════════════════════════════╗
# ║  CÓMO CAMBIAR O AGREGAR OTRA RED WI-FI                 ║
# ╠══════════════════════════════════════════════════════════╣
# ║                                                         ║
# ║  1. Buscar la sección "Configurar Wi-Fi" más abajo.     ║
# ║                                                         ║
# ║  2. Para una RED ABIERTA (sin contraseña):              ║
# ║     Cambiar el ssid y usar key_mgmt=NONE:              ║
# ║                                                         ║
# ║       network={                                         ║
# ║           ssid="NombreDeTuRed"                          ║
# ║           key_mgmt=NONE                                 ║
# ║       }                                                 ║
# ║                                                         ║
# ║  3. Para una RED CON CONTRASEÑA (ej. hotspot celular):  ║
# ║     Cambiar ssid, agregar psk (contraseña) y usar       ║
# ║     key_mgmt=WPA-PSK:                                  ║
# ║                                                         ║
# ║       network={                                         ║
# ║           ssid="NombreDeTuRed"                          ║
# ║           psk="TuContraseña"                            ║
# ║           key_mgmt=WPA-PSK                              ║
# ║           priority=2                                    ║
# ║       }                                                 ║
# ║                                                         ║
# ║  4. "priority" indica preferencia (mayor = más alta).   ║
# ║     Si quieres que el hotspot tenga más prioridad que   ║
# ║     AlumnosFI, ponele priority=2 o más.                 ║
# ║                                                         ║
# ║  5. También hay que actualizar el grep -q "..." para    ║
# ║     que el script detecte si la red ya fue agregada.    ║
# ║                                                         ║
# ║  IMPORTANTE: La Raspberry necesita conexión a Internet  ║
# ║  (vía Wi-Fi) para que el Bot de Telegram funcione.      ║
# ║  Si solo tenés Ethernet al PLC y no hay Wi-Fi con       ║
# ║  salida a Internet, el bot NO podrá enviar mensajes.    ║
# ╚══════════════════════════════════════════════════════════╝

echo "========================================"
echo "🔧 Configurando Redes de la Raspberry Pi"
echo "========================================"

# 1. Configurar Wi-Fi Abierto
echo "📡 1. Agregando red Wi-Fi 'AlumnosFI'..."
WPA_FILE="/etc/wpa_supplicant/wpa_supplicant.conf"

if grep -q "AlumnosFI" "$WPA_FILE"; then
    echo "✅ La red AlumnosFI ya estaba configurada."
else
    sudo bash -c "cat >> $WPA_FILE" << EOF

network={
    ssid="AlumnosFI"
    key_mgmt=NONE
}
EOF
    echo "✅ Red AlumnosFI añadida."
fi

# 2. Configurar Prioridad de Redes (Métricas)
echo "🚦 2. Configurando prioridad de rutas (Wi-Fi sobre Ethernet)..."
DHCP_FILE="/etc/dhcpcd.conf"

if grep -q "metric 10" "$DHCP_FILE"; then
    echo "✅ Las métricas de enrutamiento ya estaban configuradas."
else
    sudo bash -c "cat >> $DHCP_FILE" << EOF

# Prioridades configuradas por SCADA Deploy
interface wlan0
metric 10

interface eth0
metric 200
EOF
    echo "✅ Métricas de red aplicadas."
fi

echo "========================================"
echo "🎉 ¡Configuración completada exitosamente!"
echo "🔄 Aplicando cambios en la red (esto puede tomar unos segundos)..."

sudo wpa_cli -i wlan0 reconfigure > /dev/null 2>&1
# Reiniciamos el demonio DHCPD para que tomen efecto las métricas sin reiniciar la Pi
sudo systemctl restart dhcpcd > /dev/null 2>&1 || true

echo "🌐 Red reiniciada. Puedes verificar si hay internet con 'ping google.com'."
