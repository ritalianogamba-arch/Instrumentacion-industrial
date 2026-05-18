@echo off
for /f "usebackq tokens=*" %%i in (`powershell -command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set CURRENT_DATE=%%i
echo The date is: %CURRENT_DATE%
