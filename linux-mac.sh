#!/usr/bin/env bash
set -euo pipefail

WORKSHOP_TAR="workshop-vscode.tar"
WORKSHOP_IMAGE="atelier-pm:latest"
GDRIVE_FILE_ID="1ICnWeiJUiLO6mo2xp8c6RKvFo4--CdlY"
GDRIVE_URL="https://drive.google.com/uc?export=download&id=${GDRIVE_FILE_ID}"

info() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*"; }

command -v docker >/dev/null 2>&1 || DOCKER_MISSING=1 || true

if [[ "${DOCKER_MISSING:-0}" -eq 1 ]]; then
  info "Docker n'est pas installé. Installation en cours..."

  OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
  if [[ "$OS" == "darwin" ]]; then
    ARCH="$(uname -m)"
    [[ "$ARCH" == "arm64" ]] && DOCKER_ARCH="arm64" || DOCKER_ARCH="amd64"
    info "Téléchargement de Docker Desktop pour macOS ($DOCKER_ARCH)..."
    curl -L "https://desktop.docker.com/mac/main/${DOCKER_ARCH}/Docker.dmg" -o /tmp/Docker.dmg
    info "Montage de l'image..."
    hdiutil attach /tmp/Docker.dmg >/dev/null
    info "Copie de Docker.app vers /Applications..."
    cp -R /Volumes/Docker/Docker.app /Applications
    hdiutil detach /Volumes/Docker >/dev/null
    info "Docker Desktop installé. Lance-le puis relance ce script."
    exit 1
  elif [[ "$OS" == "linux" ]]; then
    info "Installation de Docker Engine sur Linux (script officiel)..."
    curl -fsSL https://get.docker.com | sh
    info "Ajout de l'utilisateur au groupe docker (déconnexion/reconnexion requise)..."
    if command -v sudo >/dev/null 2>&1; then
      sudo usermod -aG docker "$USER" || true
    else
      usermod -aG docker "$USER" || true
    fi
  else
    warn "OS non supporté: $OS"
    exit 1
  fi
else
  info "Docker est déjà installé: $(docker --version)"
fi

if ! docker info >/dev/null 2>&1; then
  warn "Docker est installé mais le moteur ne répond pas."
  warn "Lance Docker Desktop puis relance ce script."
  exit 1
fi

if [[ ! -f "$WORKSHOP_TAR" ]]; then
  info "Téléchargement de l'image depuis Google Drive..."
  curl -L "https://drive.usercontent.google.com/download?id=${GDRIVE_FILE_ID}&export=download&confirm=t" -o "$WORKSHOP_TAR"
else
  info "Archive déjà présente: $WORKSHOP_TAR"
fi

if ! tar -tf "$WORKSHOP_TAR" >/dev/null 2>&1; then
  warn "Le fichier téléchargé n'est pas une archive TAR valide."
  warn "Google Drive a probablement renvoyé une page HTML (partage ou confirmation)."
  warn "Vérifie que le fichier est bien partagé en \"Anyone with the link\"."
  warn "Sinon, télécharge-le manuellement et place '$WORKSHOP_TAR' à côté du script."
  exit 1
fi

info "Chargement de l'image Docker..."
docker load -i "$WORKSHOP_TAR"

info "Lancement du conteneur..."
docker run -p 8080:8080 "$WORKSHOP_IMAGE"
