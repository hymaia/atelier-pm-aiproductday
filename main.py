"""
main.py — CLI principal du PM Meeting Assistant

Lance automatiquement l'indexation si nécessaire, puis propose :
  [1] Briefing du matin
  [2] Préparer une réunion

Usage :
    python main.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import box
from rich.rule import Rule
from rich.text import Text
from rich.align import Align

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from indexer import run_indexer, load_index, scan_data_directory, generate_file_id
from skills import morning_briefing, prepare_meeting

console = Console()

BANNER = """
[bold blue]╔══════════════════════════════════════════════╗
║      PM Meeting Assistant  ·  Demo           ║
║      Propulsé par Claude Opus 4.6            ║
╚══════════════════════════════════════════════╝[/bold blue]
"""


def check_and_update_index() -> tuple[int, int]:
    """
    Vérifie si des fichiers non indexés existent et lance l'indexation si besoin.
    Retourne (nouveaux, total).
    """
    index = load_index()
    indexed_ids = {entry["id"] for entry in index}

    # Scanner les fichiers disponibles
    all_files = scan_data_directory()
    new_files = [f for f in all_files if generate_file_id(f) not in indexed_ids]

    if new_files:
        console.print(f"\n[yellow]⚡ {len(new_files)} nouveau(x) fichier(s) détecté(s) — mise à jour de l'index...[/yellow]")
        nouveaux, deja_connus = run_indexer(reset=False)
        console.print(f"[green]✓ Index mis à jour : {nouveaux} nouveau(x) fichier(s) indexé(s)[/green]")
        index = load_index()
    else:
        console.print(f"[dim]Index à jour ({len(index)} fichier(s) indexé(s))[/dim]")

    return len(new_files), len(index)


def show_index_summary(index: list[dict]) -> None:
    """Affiche un résumé de l'index sous forme de tableau."""
    if not index:
        return

    table = Table(
        title="Fichiers indexés",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Date", width=12)
    table.add_column("Client", width=18)
    table.add_column("Titre", width=35)
    table.add_column("Ko", width=6, justify="right")

    # Trier par type, puis date
    sorted_index = sorted(index, key=lambda x: (x.get("type") or "", x.get("date") or ""))

    for entry in sorted_index:
        type_colors = {
            "calendar": "blue",
            "transcript": "green",
            "note": "yellow",
            "summary": "magenta",
        }
        entry_type = entry.get("type", "?")
        color = type_colors.get(entry_type, "white")

        table.add_row(
            f"[{color}]{entry_type}[/{color}]",
            entry.get("date") or "—",
            entry.get("client") or "—",
            (entry.get("title") or "—")[:35],
            str(entry.get("size_kb", "?")),
        )

    console.print(table)


def menu_choice() -> int:
    """Affiche le menu principal et retourne le choix de l'utilisateur."""
    console.print()
    console.print(Panel(
        "[1] [bold green]Briefing du matin[/bold green]\n"
        "    Agenda du jour + contexte de chaque réunion\n\n"
        "[2] [bold yellow]Préparer une réunion[/bold yellow]\n"
        "    Historique, participants, last touchpoint\n\n"
        "[0] [dim]Quitter[/dim]",
        title="[bold]Que souhaitez-vous faire ?[/bold]",
        border_style="blue",
        padding=(1, 3),
    ))

    while True:
        try:
            choice = IntPrompt.ask("\n[bold]Votre choix[/bold]", default=1)
            if choice in (0, 1, 2):
                return choice
            console.print("[red]Entrez 0, 1 ou 2[/red]")
        except (KeyboardInterrupt, EOFError):
            return 0


def run_morning_briefing() -> None:
    """Lance le skill briefing du matin."""
    today = date.today().isoformat()
    console.print(f"\n[dim]Date par défaut : {today}[/dim]")

    date_input = Prompt.ask(
        f"[bold]Date du briefing[/bold]",
        default=today,
    )

    # Valider le format de date
    import re
    if not re.match(r"\d{4}-\d{2}-\d{2}", date_input):
        console.print("[red]Format de date invalide. Utilisez YYYY-MM-DD[/red]")
        return

    morning_briefing.run(date_input)


def run_prepare_meeting() -> None:
    """Lance le skill préparer une réunion."""
    console.print()
    console.print("[dim]Exemples : 'Acme Corp', 'NovaTech', 'Julie Chen', 'revue trimestrielle'[/dim]")
    query = Prompt.ask("[bold]Nom de la réunion ou du participant[/bold]")

    if not query.strip():
        console.print("[red]Veuillez entrer un nom.[/red]")
        return

    prepare_meeting.run(query.strip())


def main() -> None:
    """Point d'entrée principal."""
    # Afficher le banner
    console.print(BANNER)

    # Vérifier et mettre à jour l'index si nécessaire
    try:
        _, total = check_and_update_index()
    except Exception as e:
        console.print(f"[red]Erreur lors de l'indexation : {e}[/red]")
        total = 0

    # Afficher un résumé de l'index
    index = load_index()
    if index:
        show_index_summary(index)
    else:
        console.print("[yellow]⚠ Aucun fichier indexé. Ajoutez des fichiers dans le dossier data/[/yellow]")

    # Boucle principale du menu
    while True:
        choice = menu_choice()

        if choice == 0:
            console.print("\n[dim]Au revoir ![/dim]\n")
            break

        elif choice == 1:
            try:
                run_morning_briefing()
            except KeyboardInterrupt:
                console.print("\n[dim]Annulé.[/dim]")
            except RuntimeError:
                pass  # Message d'erreur déjà affiché par get_client()
            except Exception as e:
                console.print(f"\n[red]Erreur : {e}[/red]")
                if "--debug" in sys.argv:
                    import traceback
                    traceback.print_exc()

        elif choice == 2:
            try:
                run_prepare_meeting()
            except KeyboardInterrupt:
                console.print("\n[dim]Annulé.[/dim]")
            except RuntimeError:
                pass  # Message d'erreur déjà affiché par get_client()
            except Exception as e:
                console.print(f"\n[red]Erreur : {e}[/red]")
                if "--debug" in sys.argv:
                    import traceback
                    traceback.print_exc()

        # Proposer une nouvelle action après chaque exécution
        console.print()
        again = Prompt.ask(
            "[dim]Retourner au menu ?[/dim]",
            choices=["o", "n"],
            default="o",
        )
        if again.lower() != "o":
            console.print("\n[dim]Au revoir ![/dim]\n")
            break


if __name__ == "__main__":
    main()
