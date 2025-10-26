@echo off
title Generar ejecutable del juego "Adivina Quien - Hollow Knight"
echo ===============================================================
echo     Creando ejecutable del juego Adivina Quien - Hollow Knight
echo ===============================================================
echo.

:: --- LIMPIEZA DE COMPILACIONES ANTERIORES ---
echo Limpiando archivos antiguos...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Adivina_Quien_Hollow_Knight.spec del /q Adivina_Quien_Hollow_Knight.spec
if exist __pycache__ rmdir /s /q __pycache__
echo.

:: --- ACTIVAR ENTORNO VIRTUAL (SI EXISTE) ---
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call "venv\Scripts\activate.bat"
) else (
    echo Continuando con el entorno de Python global.
)
echo.

:: --- ACTUALIZAR PIP (Recomendado por tu log) ---
echo Actualizando pip...
python -m pip install --upgrade pip >nul
echo.

:: --- ASEGURAR DEPENDENCIAS NECESARIAS ---
echo Instalando/verificando dependencias (pillow, customtkinter, pyinstaller, pyglet)...
pip install pillow customtkinter pyinstaller pyglet >nul
echo.

:: --- GENERAR EJECUTABLE ---
echo Compilando el juego (esto puede tardar unos minutos)...

:: Este es el comando de compilacion.
:: Todos los argumentos deben estar en lineas seguidas
:: terminando con '^' (excepto la ultima).
:: NO pongas comentarios (:: o rem) entre 'python -m PyInstaller' y el .py
python -m PyInstaller --onefile --noconsole ^
 --name "Adivina_Quien_Hollow_Knight" ^
 --hidden-import=PIL.ImageTk ^
 --hidden-import=darkdetect ^
 --hidden-import=pyglet ^
 --hidden-import=pyglet.font ^
 --hidden-import=pyglet.media ^
 --hidden-import=pyglet.media.drivers.directsound ^
 --hidden-import=pyglet.media.drivers.waveout ^
 --add-data "hollow_knight_data.json;." ^
 --add-data "fondo.jpg;." ^
 --add-data "CinzelDecorative-Regular.ttf;." ^
 Adivina_Quien_Hollow_Knight_gui.py

:: --- MOVER Y LIMPIAR ---
echo.
echo Moviendo el ejecutable generado...
if exist "dist\Adivina_Quien_Hollow_Knight.exe" (
    move /Y "dist\Adivina_Quien_Hollow_Knight.exe" ".\Adivina_Quien_Hollow_Knight.exe" >nul
    echo ===============================================================
    echo.
    echo    ¡Ejecutable creado con exito!
    echo.
    echo El archivo se encuentra en esta carpeta como:
    echo Adivina_Quien_Hollow_Knight.exe
    echo.
    echo ===============================================================
) else (
    echo ---------------------------------------------------------------
    echo.
    echo    Ocurrio un error durante la compilacion.
    echo    Revisa los mensajes de error de arriba.
    echo.
    echo ---------------------------------------------------------------
)

:: Limpieza final de carpetas de compilacion
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Adivina_Quien_Hollow_Knight.spec del /q Adivina_Quien_Hollow_Knight.spec

echo.
pause