"""
claude_client.py — Helper partagé pour initialiser le client Anthropic.

Vérifie que ANTHROPIC_API_KEY est définie, avec un message d'erreur clair sinon.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import anthropic
from rich.console import Console
from rich.panel import Panel

console = Console()

# Charger le fichier .env s'il existe (sans dépendance externe)
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            # Toujours charger depuis .env (écrase les valeurs vides de l'environnement)
            if not os.environ.get(key.strip()):
                os.environ[key.strip()] = value.strip()


def get_client() -> anthropic.Anthropic:
    """
    Retourne un client Anthropic initialisé.

    Si ANTHROPIC_API_KEY n'est pas définie, affiche un message d'aide
    et lève une exception claire.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if not api_key:
        console.print(Panel(
            "[bold red]Clé API Anthropic manquante[/bold red]\n\n"
            "La variable d'environnement [bold]ANTHROPIC_API_KEY[/bold] n'est pas définie.\n\n"
            "Pour la définir dans votre terminal :\n"
            "  [bold cyan]export ANTHROPIC_API_KEY=\"sk-ant-...[/bold cyan]\"\n\n"
            "Obtenez votre clé sur : [link]https://console.anthropic.com/settings/keys[/link]",
            border_style="red",
            title="❌ Erreur d'authentification",
        ))
        raise RuntimeError(
            "ANTHROPIC_API_KEY non définie. "
            "Exécutez : export ANTHROPIC_API_KEY=\"votre-clé\""
        )

    return anthropic.Anthropic(api_key=api_key)
