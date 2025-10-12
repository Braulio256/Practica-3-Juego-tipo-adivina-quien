@echo off
title Generar ejecutable del juego "Adivina Quien - Hollow Knight"
echo ===============================================================
echo     Creando ejecutable del juego Adivina Quien - Hollow Knight
echo ===============================================================
echo.

:: Limpieza de compilaciones anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Adivina_Quien_Hollow_Knight_gui.spec del /q Adivina_Quien_Hollow_Knight_gui.spec
if exist __pycache__ rmdir /s /q __pycache__

:: Asegurar dependencias necesarias
echo Instalando dependencias necesarias...
pip install pillow customtkinter pyinstaller >nul

:: Generar ejecutable
echo.
echo Compilando el juego...
python -m PyInstaller --onefile --noconsole ^
--hidden-import=PIL ^
--hidden-import=PIL.Image ^
--add-data "hollow_knight_data.json;." ^
--add-data "fondo.jpg;." ^
--add-data "CinzelDecorative-Regular.ttf;." ^
Adivina_Quien_Hollow_Knight_gui.py

:: Mover el ejecutable a la carpeta raíz para fácil acceso
echo.
echo Moviendo el ejecutable generado...
if exist "dist\Adivina_Quien_Hollow_Knight_gui.exe" (
    move /Y "dist\Adivina_Quien_Hollow_Knight_gui.exe" ".\Adivina_Quien_Hollow_Knight.exe" >nul
    echo ✅ ¡Ejecutable creado con éxito!
    echo.
    echo El archivo se encuentra como: Adivina_Quien_Hollow_Knight.exe
) else (
    echo ❌ Ocurrió un error durante la compilación.
)

pause
