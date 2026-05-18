#!/bin/bash
# Script de inicio automático para servicios PLC

echo "⏳ Esperando que la red esté lista..."
sleep 5

cd /home/admin/plc_server
source venv/bin/activate

echo "📡 Iniciando Ngrok en segundo plano..."
killall ngrok 2>/dev/null || true
ngrok http http://127.0.0.1:8080 > /dev/null 2>&1 &

echo "🚀 Iniciando aplicación SCADA (Flask + Bot) en primer plano..."
# Al ejecutarlo sin '&', el script bloquea y mantiene vivo el servicio systemd
python3 app.py
