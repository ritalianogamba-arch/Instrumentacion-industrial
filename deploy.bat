@echo off
echo ========================================
echo    ACTUALIZADOR RASPBERRY PLC SERVER
echo ========================================
echo.

set "RASPBERRY_HOST=plc-server.local"
set "RASPBERRY_USER=admin"
set "RASPBERRY_DIR=~/plc_server"

echo Conectando a Raspberry Pi...
ping -n 1 %RASPBERRY_HOST% >nul

if errorlevel 1 (
    echo ERROR: No se puede conectar a %RASPBERRY_HOST%
    echo Verifica que la Raspberry este encendida y en la red
    pause
    exit /b 1
)

echo OK: Raspberry encontrada
echo.

echo Enviando archivos base...
:: Enviamos los archivos Python principales y requirements
scp app.py api_routes.py bot_telegram.py mocks.py modbus_core.py supervisors.py requirements.txt %RASPBERRY_USER%@%RASPBERRY_HOST%:%RASPBERRY_DIR%/

:: Enviar certificados SSL solo si existen
if exist server.crt (
    echo Enviando certificados SSL...
    scp server.crt server.key %RASPBERRY_USER%@%RASPBERRY_HOST%:%RASPBERRY_DIR%/
)

echo.
echo Enviando carpetas de modulos y recursos...
:: Enviamos las carpetas de configuracion, modelos, estaticos y templates
scp -r config models static templates %RASPBERRY_USER%@%RASPBERRY_HOST%:%RASPBERRY_DIR%/

echo.
echo Instalando/Actualizando dependencias en Raspberry...
ssh %RASPBERRY_USER%@%RASPBERRY_HOST% "pip install -r %RASPBERRY_DIR%/requirements.txt"

echo.
echo Reiniciando servicios en Raspberry...
:: Reiniciar el servidor principal (ahora incluye el Bot de Telegram)
ssh %RASPBERRY_USER%@%RASPBERRY_HOST% "sudo systemctl restart plc-server.service"

echo.
echo ACTUALIZACION COMPLETADA!
echo El servidor ahora utiliza app.py como entrada principal (incluye Bot de Telegram).
echo.
echo Usa /link en Telegram para obtener la nueva URL si cambio la IP.
echo.
pause
