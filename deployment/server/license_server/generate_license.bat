@echo off
REM Script batch pour générer une licence sur Windows
REM Utilise le launcher Python Windows (py)

if "%1"=="" (
    echo Usage: generate_license.bat config.json [output_file]
    echo.
    echo Exemple: generate_license.bat example_config.json license.txt
    exit /b 1
)

set CONFIG_FILE=%1
set OUTPUT_FILE=%2

if "%OUTPUT_FILE%"=="" (
    py generate_license.py --config %CONFIG_FILE%
) else (
    py generate_license.py --config %CONFIG_FILE% --output %OUTPUT_FILE%
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Licence générée avec succès
) else (
    echo.
    echo ✗ Erreur lors de la génération de la licence
    echo.
    echo Vérifiez:
    echo - Que le fichier de configuration existe
    echo - Que la clé privée existe dans ./keys/private_key.pem
    echo - Que Python et cryptography sont installés
)

pause
