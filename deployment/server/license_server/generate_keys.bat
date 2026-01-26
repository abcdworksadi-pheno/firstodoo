@echo off
REM Script batch pour générer les clés sur Windows
REM Utilise le launcher Python Windows (py)

echo Génération des clés Ed25519 pour le système de licence ABCD...
echo.

py generate_keys.py --output-dir ./keys

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Clés générées avec succès dans le répertoire ./keys
    echo.
    echo ⚠️  IMPORTANT: La clé privée (private_key.pem) ne doit JAMAIS être partagée!
) else (
    echo.
    echo ✗ Erreur lors de la génération des clés
    echo.
    echo Vérifiez que Python est installé:
    echo - Téléchargez depuis https://www.python.org/downloads/
    echo - Ou installez depuis Microsoft Store
    echo - Ou utilisez: py -m pip install cryptography
)

pause
