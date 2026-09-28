@echo off
:: Cambia automáticamente al directorio donde se encuentra este archivo .bat
cd /d "%~dp0"

:: Ejecuta el robot de Python
python robot.py

pause