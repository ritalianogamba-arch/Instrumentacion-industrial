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

echo Preparando lista de archivos a transferir...
set "ARCHIVOS=app.py api_routes.py bot_telegram.py modbus_core.py validate_addresses.py inicio_servicios.sh setup_red.sh requirements.txt config models static templates MODBUS_MAPPING.md ARCHITECTURE.md README.md"

:: Anexar .env si existe (no está en git)
if exist .env (
    set "ARCHIVOS=%ARCHIVOS% .env"
)

:: Anexar certificados si existen
if exist server.crt (
    set "ARCHIVOS=%ARCHIVOS% server.crt server.key"
)

echo.
echo ========================================
echo [ACCION 1/2] TRANSFERENCIA DE ARCHIVOS
echo Te pedira la clave de la Raspberry una vez.
echo ========================================
scp -r %ARCHIVOS% %RASPBERRY_USER%@%RASPBERRY_HOST%:%RASPBERRY_DIR%/

echo.
echo ========================================
echo [ACCION 2/2] INSTALACION Y REINICIO
echo Te pedira la clave por ultima vez.
echo ========================================
echo Sincronizando hora con la Raspberry Pi...
for /f "usebackq tokens=*" %%i in (`powershell -command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set CURRENT_DATE=%%i
ssh %RASPBERRY_USER%@%RASPBERRY_HOST% "sudo date -s '%CURRENT_DATE%'; if [ -f %RASPBERRY_DIR%/.env ]; then sed -i 's/\r$//' %RASPBERRY_DIR%/.env; fi; sed -i 's/\r$//' %RASPBERRY_DIR%/inicio_servicios.sh; chmod +x %RASPBERRY_DIR%/inicio_servicios.sh; sudo systemctl restart plc-server.service"

echo.
echo ACTUALIZACION COMPLETADA!
echo El servidor ha sido actualizado y reiniciado exitosamente.
echo.
echo Usa /link en Telegram para obtener la nueva URL si cambio la IP.
echo.
pause
