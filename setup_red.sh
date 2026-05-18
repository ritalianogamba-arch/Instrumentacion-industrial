#!/bin/bash
# Script de configuración automática de red para la Raspberry Pi
# Ejecutar con: sudo bash setup_red.sh

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
