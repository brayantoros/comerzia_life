@echo off
cd /d "%~dp0"
echo ========================================================
echo   PRUEBAS FUNCIONALES - PROYECTO PRODUCTIVO COMERZIA
echo ========================================================
echo.

echo 1. Ejecutando suite de pruebas unitarias y funcionales...
python tests_funcionales.py

echo.
echo 2. Generando reportes de Comerzia (PDF y Excel)...
python report.py

echo.
echo ========================================================
echo   PROCESO TERMINADO
echo ========================================================
pause
