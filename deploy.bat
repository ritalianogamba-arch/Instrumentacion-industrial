@echo off
echo ========================================
echo    ACTUALIZADOR RASPBERRY PLC SERVER
echo ========================================
echo.

set "RASPBERRY_HOST=plc-server.local"
set "RASPBERRY_USER=admin"
set "RASPBERRY_DIR=~/plc_server"

echo Conectando a Raspberry Pi...
ping -n 3 %RASPBERRY_HOST% >nul

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

echo.
echo Enviando carpetas de modulos y recursos...
:: Enviamos las carpetas de configuracion, modelos, estaticos y templates
:: Nota: scp -r copiara las carpetas dentro de RASPBERRY_DIR
scp -r config models static templates %RASPBERRY_USER%@%RASPBERRY_HOST%:%RASPBERRY_DIR%/

echo.
echo Reiniciando servicios en Raspberry...
ssh %RASPBERRY_USER%@%RASPBERRY_HOST% "cd %RASPBERRY_DIR% && sudo systemctl restart plc-server.service"

echo.
echo ACTUALIZACION COMPLETADA!
echo El servidor ahora utiliza app.py como entrada principal.
echo Usa /link en Telegram para obtener la nueva URL si cambio la IP.
echo.
pause
