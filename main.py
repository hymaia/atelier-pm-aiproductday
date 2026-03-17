"""
main.py — CLI principal du PM Meeting Assistant (mode conversationnel)

L'utilisateur pose une question en langage naturel.
Claude analyse la demande, choisit le bon skill (tool use), et l'exécute.

Usage :
    python main.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from indexer import run_indexer, load_index, scan_data_directory, generate_file_id
from skills import morning_briefing, prepare_meeting
from skills.claude_client import get_client

console = Console()

BANNER = """
[bold blue]╔══════════════════════════════════════════════╗
║      PM Meeting Assistant  ·  Demo           ║
║      Propulsé par Claude Opus 4.6            ║
╚══════════════════════════════════════════════╝[/bold blue]
"""

# --- Définition des tools exposés à Claude ---

TOOLS = [
    {
        "name": "morning_briefing",
        "description": (
            "Génère le briefing du matin : agenda du jour avec contexte et actions en cours "
            "pour chaque réunion. À utiliser quand l'utilisateur demande son agenda, "
            "son briefing, ses réunions du jour, ce qu'il a aujourd'hui, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": (
                        "Date du briefing au format YYYY-MM-DD. "
                        f"Par défaut aujourd'hui : {date.today().isoformat()}"
                    ),
                }
            },
            "required": [],
        },
    },
    {
        "name": "prepare_meeting",
        "description": (
            "Prépare une fiche de réunion : historique des interactions, participants, "
            "last touchpoint, actions en cours, questions à poser. "
            "À utiliser quand l'utilisateur mentionne un client, un participant, "
            "une réunion spécifique, ou demande de se préparer pour un call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Nom du client, participant ou réunion à rechercher. "
                        "Exemples : 'Acme Corp', 'NovaTech', 'Julie Chen', 'review trimestrielle'."
                    ),
                }
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = f"""Tu es l'assistant d'un Product Manager. Tu as accès à deux outils :
- morning_briefing : pour tout ce qui concerne l'agenda du jour et le briefing
- prepare_meeting : pour préparer une réunion spécifique (client, participant, sujet)

La date d'aujourd'hui est {date.today().isoformat()}.
Analyse la demande de l'utilisateur et appelle le bon outil avec les bons paramètres.
Ne réponds jamais en texte pur — utilise toujours un outil."""


def check_and_update_index() -> int:
    """Met à jour l'index si nécessaire. Retourne le total de fichiers indexés."""
    index = load_index()
    indexed_ids = {entry["id"] for entry in index}
    all_files = scan_data_directory()
    new_files = [f for f in all_files if generate_file_id(f) not in indexed_ids]

    if new_files:
        console.print(f"\n[yellow]⚡ {len(new_files)} nouveau(x) fichier(s) — mise à jour de l'index...[/yellow]")
        run_indexer(reset=False)
        console.print(f"[green]✓ Index mis à jour[/green]")

    index = load_index()
    return len(index)


def route_and_execute(user_message: str) -> None:
    """
    Envoie le message à Claude avec les tools définis.
    Claude choisit le tool approprié, on l'exécute localement.
    """
    client = get_client()

    console.print("\n[dim]Analyse de votre demande...[/dim]")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[{"role": "user", "content": user_message}],
    )

    # Chercher le tool_use dans la réponse
    tool_call = next(
        (block for block in response.content if block.type == "tool_use"),
        None,
    )

    if tool_call is None:
        # Claude a répondu en texte (cas imprévu)
        for block in response.content:
            if hasattr(block, "text"):
                console.print(block.text)
        return

    tool_name = tool_call.name
    tool_input = tool_call.input

    console.print(Rule(f"[dim]skill → {tool_name}[/dim]", style="dim"))

    if tool_name == "morning_briefing":
        target_date = tool_input.get("date") or date.today().isoformat()
        morning_briefing.run(target_date)

    elif tool_name == "prepare_meeting":
        query = tool_input.get("query", "")
        prepare_meeting.run(query)

    else:
        console.print(f"[red]Outil inconnu : {tool_name}[/red]")


def main() -> None:
    """Point d'entrée principal — boucle conversationnelle."""
    console.print(BANNER)

    # Indexation automatique au démarrage
    try:
        total = check_and_update_index()
        console.print(f"[dim]{total} fichier(s) disponibles dans l'index[/dim]\n")
    except Exception as e:
        console.print(f"[red]Erreur indexation : {e}[/red]")

    console.print("[bold]Posez votre question[/bold] [dim](ex: 'Montre-moi mon agenda', 'Prépare-moi pour Acme')[/dim]")
    console.print("[dim]Tapez 'quit' ou Ctrl+C pour quitter[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]>[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Au revoir ![/dim]\n")
            break

        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("\n[dim]Au revoir ![/dim]\n")
            break

        try:
            route_and_execute(user_input)
        except KeyboardInterrupt:
            console.print("\n[dim]Annulé.[/dim]")
        except RuntimeError:
            pass  # Message d'erreur déjà affiché par get_client()
        except Exception as e:
            console.print(f"\n[red]Erreur : {e}[/red]")
            if "--debug" in sys.argv:
                import traceback
                traceback.print_exc()

        console.print()


if __name__ == "__main__":
    main()
