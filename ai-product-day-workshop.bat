@echo off
setlocal enabledelayedexpansion

set WORKSHOP_TAR=atelier-pm.tar
set WORKSHOP_IMAGE=atelier-pm:latest
set GDRIVE_FILE_ID=19XSc3JQJ0yE4fet6F2kYhe9U3H8RJ6fp

:: ── Docker installé ? ───────────────────────────────────────────────────────
where docker >nul 2>&1
if errorlevel 1 (
    echo [INFO] Docker n'est pas installe. Installation en cours...

    if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
        set DOCKER_ARCH=arm64
    ) else (
        set DOCKER_ARCH=amd64
    )

    echo [INFO] Telechargement de Docker Desktop pour Windows ^(!DOCKER_ARCH!^)...
    curl -L --ssl-no-revoke "https://desktop.docker.com/win/main/!DOCKER_ARCH!/Docker%%20Desktop%%20Installer.exe" -o "%TEMP%\DockerInstaller.exe"
    if errorlevel 1 (
        echo [ERREUR] Echec du telechargement de Docker Desktop.
        echo [ERREUR] Telecharge-le manuellement depuis https://www.docker.com/products/docker-desktop/ et relance ce script.
        exit /b 1
    )
    if not exist "%TEMP%\DockerInstaller.exe" (
        echo [ERREUR] Fichier d'installation introuvable apres telechargement.
        exit /b 1
    )

    echo [INFO] Installation silencieuse de Docker Desktop...
    "%TEMP%\DockerInstaller.exe" install --quiet --accept-license

    echo [INFO] Docker Desktop installe. Redemarre si demande, lance Docker Desktop, puis relance ce script.
    exit /b 1
) else (
    for /f "tokens=*" %%v in ('docker --version') do echo [INFO] Docker est deja installe: %%v
)

:: ── Moteur Docker actif ? ────────────────────────────────────────────────────
docker info >nul 2>&1
if errorlevel 1 (
    echo [WARN] Docker est installe mais le moteur ne repond pas.
    echo [WARN] Lance Docker Desktop puis relance ce script.
    exit /b 1
)

:: ── Telechargement de l'image ────────────────────────────────────────────────
if not exist "%WORKSHOP_TAR%" (
    echo [INFO] Telechargement de l'image depuis Google Drive...
    curl -L --ssl-no-revoke "https://drive.usercontent.google.com/download?id=%GDRIVE_FILE_ID%&export=download&confirm=t" -o "%WORKSHOP_TAR%"
) else (
    echo [INFO] Archive deja presente : %WORKSHOP_TAR%
)

:: ── Validation du tar ────────────────────────────────────────────────────────
tar -tf "%WORKSHOP_TAR%" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Le fichier telecharge n'est pas une archive TAR valide.
    echo [WARN] Google Drive a probablement renvoye une page HTML ^(partage ou confirmation^).
    echo [WARN] Verifie que le fichier est bien partage en "Anyone with the link".
    echo [WARN] Sinon, telecharge-le manuellement et place '%WORKSHOP_TAR%' a cote du script.
    exit /b 1
)

:: ── Chargement et lancement ──────────────────────────────────────────────────
echo [INFO] Chargement de l'image Docker...
docker load -i "%WORKSHOP_TAR%"

echo [INFO] Lancement du conteneur...
docker run -p 8080:8080 "%WORKSHOP_IMAGE%"

endlocal
