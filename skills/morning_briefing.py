"""
morning_briefing.py — Skill 1 : Briefing du matin

Génère un briefing structuré pour la journée en cours :
- Agenda du jour avec heure et titre de chaque réunion
- Pour chaque réunion : contexte issu de l'historique (dernière interaction, actions en cours)

Pattern deux étapes :
  1. Filtrage sur index.json (jamais de lecture de fichiers)
  2. Lecture ciblée des fichiers retenus (max 10 au total)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.rule import Rule

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.claude_client import get_client

from loaders import calendar_loader, transcript_loader, notes_loader, summary_loader

console = Console()
BASE_DIR = Path(__file__).parent.parent
INDEX_FILE = BASE_DIR / "index.json"


def load_index() -> list[dict]:
    """Charge l'index depuis index.json."""
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """Normalise un texte pour la comparaison : minuscules, sans accents."""
    import unicodedata
    text = text.lower()
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return text


def filter_by_date(index: list[dict], target_date: str) -> list[dict]:
    """Étape 1a : filtrer l'index sur une date précise."""
    return [e for e in index if e.get("date") == target_date]


def filter_by_client_or_participants(
    index: list[dict],
    client: str | None,
    participants: list[str],
    exclude_ids: set[str] | None = None,
    max_results: int = 3,
) -> list[dict]:
    """
    Étape 1b : filtrer l'index sur le client ou les participants.
    Retourne les entrées les plus récentes en premier.
    """
    if exclude_ids is None:
        exclude_ids = set()

    client_norm = normalize_text(client) if client else ""
    participants_norm = [normalize_text(p) for p in participants]

    scored = []
    for entry in index:
        if entry["id"] in exclude_ids:
            continue
        score = 0

        # Match sur le client
        entry_client = normalize_text(entry.get("client") or "")
        if client_norm and client_norm in entry_client:
            score += 2
        elif client_norm and entry_client and any(
            part in entry_client or entry_client in part
            for part in client_norm.split()
            if len(part) > 2
        ):
            score += 1

        # Match sur les participants
        entry_participants = [normalize_text(p) for p in (entry.get("participants") or [])]
        for pnorm in participants_norm:
            pnorm_short = pnorm.split()[0] if pnorm.split() else pnorm
            for ep in entry_participants:
                if pnorm_short in ep or ep in pnorm:
                    score += 1
                    break

        if score > 0:
            scored.append((score, entry.get("date") or "", entry))

    # Trier par score décroissant, puis par date décroissante
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [entry for _, _, entry in scored[:max_results]]


def load_files(entries: list[dict]) -> list[dict]:
    """
    Étape 2 : charge les fichiers listés dans les entrées d'index.
    Retourne une liste de contenus normalisés.
    """
    loaders = {
        "calendar": calendar_loader,
        "transcript": transcript_loader,
        "note": notes_loader,
        "summary": summary_loader,
    }

    results = []
    for entry in entries:
        file_type = entry.get("type")
        loader = loaders.get(file_type)
        if not loader:
            continue

        filepath = BASE_DIR / entry["path"]
        try:
            loaded = loader.load(filepath)
            for item in loaded:
                item["_source_type"] = file_type
                item["_source_path"] = entry["path"]
                item["_index_client"] = entry.get("client")
            results.extend(loaded)
        except Exception as e:
            console.print(f"  ⚠ Erreur chargement {entry['path']}: {e}", style="yellow")

    return results


def generate_briefing_with_claude(
    target_date: str,
    meetings: list[dict],
    historical_data: dict[str, list[dict]],
) -> str:
    """
    Utilise Claude pour générer un briefing structuré et naturel.

    Args:
        target_date: Date cible (ex: "2026-03-17")
        meetings: Liste des réunions du jour
        historical_data: Dict {meeting_title: [fichiers historiques]}
    """
    client = get_client()

    # Construire le contexte pour Claude
    meetings_text = []
    for m in meetings:
        meeting_info = f"""
### {m.get('start_time', '?')} - {m.get('title', 'Sans titre')}
- Participants : {', '.join(m.get('participants', [])) or 'Non spécifié'}
- Lieu : {m.get('location', 'Non spécifié')}
- Description : {m.get('description', m.get('raw_text', ''))[:200]}
"""
        meetings_text.append(meeting_info)

    historical_text = []
    for meeting_title, history_items in historical_data.items():
        if not history_items:
            historical_text.append(f"\n### Historique pour '{meeting_title}' : Aucun historique trouvé")
            continue

        historical_text.append(f"\n### Historique pour '{meeting_title}' :")
        for item in history_items[:3]:
            item_text = f"""
**{item.get('_source_type', 'fichier')} du {item.get('date', 'date inconnue')} — {item.get('title', '')}**
{item.get('raw_text', '')[:600]}
"""
            if item.get('decisions'):
                item_text += f"\nDécisions : {item['decisions'][:200]}"
            if item.get('actions'):
                item_text += f"\nActions : {item['actions'][:300]}"
            historical_text.append(item_text)

    prompt = f"""Tu es un assistant PM (Product Manager). Génère un briefing du matin pour la journée du {target_date}.

## Réunions du jour
{"".join(meetings_text)}

## Historique disponible
{"".join(historical_text)}

## Instructions
Génère un briefing professionnel et synthétique pour chaque réunion avec :

1. **Heure + Titre** (bien visible)
2. **Participants** (liste courte)
3. **Contexte** : Dernière fois qu'on s'est vus + sujet abordé (1-2 phrases max)
4. **Actions en cours** : Actions non résolues [OPEN] à mentionner si pertinent
5. **Point d'attention** : Un conseil ou signal faible à garder en tête

Format : markdown clair et lisible, rédigé comme si tu préparais un briefing pour un PM senior.
Si l'historique est vide pour une réunion, dis-le clairement et donne des conseils de préparation.
Sois concis : le briefing doit se lire en 3 minutes maximum.
"""

    console.print("\n[dim]Génération du briefing avec Claude...[/dim]")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_text = ""
        for text in stream.text_stream:
            full_text += text

    return full_text


def run(target_date: str | None = None) -> None:
    """
    Point d'entrée du skill morning briefing.

    Args:
        target_date: Date au format YYYY-MM-DD. Si None, utilise aujourd'hui.
    """
    if target_date is None:
        target_date = date.today().isoformat()

    console.print(f"\n[bold blue]📅 Briefing du matin — {target_date}[/bold blue]\n")

    # Charger l'index
    index = load_index()
    if not index:
        console.print("[yellow]⚠ Index vide. Lancez d'abord : python indexer.py[/yellow]")
        return

    # ═══ ÉTAPE 1 : Filtrage sur index.json ═══

    # 1a. Trouver les réunions du calendrier pour la date cible
    calendar_entries = [
        e for e in filter_by_date(index, target_date)
        if e.get("type") == "calendar"
    ]

    # Si pas de réunions dans l'index pour aujourd'hui, chercher dans tous les calendriers
    if not calendar_entries:
        calendar_entries = [e for e in index if e.get("type") == "calendar"]

    console.print(f"[dim]Index chargé : {len(index)} fichiers[/dim]")
    console.print(f"[dim]Fichiers calendrier identifiés : {len(calendar_entries)}[/dim]")

    # ═══ ÉTAPE 2 : Charger les fichiers calendrier ═══
    calendar_data = load_files(calendar_entries)

    # Filtrer les réunions du jour
    meetings_today = [
        item for item in calendar_data
        if item.get("date") == target_date
    ]

    if not meetings_today:
        console.print(f"[yellow]Aucune réunion trouvée pour le {target_date}.[/yellow]")
        console.print("[dim]Vérifiez votre fichier calendar.csv dans data/calendar/[/dim]")
        return

    console.print(f"[green]✓ {len(meetings_today)} réunion(s) trouvée(s) pour le {target_date}[/green]")

    # ═══ ÉTAPE 1b : Pour chaque réunion, trouver l'historique ═══
    # Règle : max 10 fichiers au total
    total_files_loaded = len(calendar_entries)
    max_remaining = max(0, 10 - total_files_loaded)
    files_per_meeting = max(1, max_remaining // max(1, len(meetings_today)))

    historical_index_entries: dict[str, list[dict]] = {}
    calendar_entry_ids = {e["id"] for e in calendar_entries}

    for meeting in meetings_today:
        meeting_title = meeting.get("title", "")
        participants = meeting.get("participants", [])

        # Extraire le nom du client depuis le titre
        client_name = None
        for word in meeting_title.split():
            if len(word) > 3 and word.istitle():
                client_name = word
                break

        # Filtrer l'historique (transcripts + notes + summaries)
        history_entries = filter_by_client_or_participants(
            [e for e in index if e.get("type") in ("transcript", "note", "summary")],
            client=client_name,
            participants=participants,
            exclude_ids=calendar_entry_ids,
            max_results=files_per_meeting,
        )

        historical_index_entries[meeting_title] = history_entries

    # Compter le total de fichiers à charger
    all_history_entries = []
    seen_ids = set()
    for entries_list in historical_index_entries.values():
        for e in entries_list:
            if e["id"] not in seen_ids:
                all_history_entries.append(e)
                seen_ids.add(e["id"])

    console.print(f"[dim]Fichiers historiques à charger : {len(all_history_entries)} (max 10)[/dim]")

    # ═══ ÉTAPE 2b : Charger les fichiers historiques ═══
    # Charger une fois, indexer par id
    all_loaded = load_files(all_history_entries[:10])
    loaded_by_path = {}
    for item in all_loaded:
        loaded_by_path[item["_source_path"]] = loaded_by_path.get(item["_source_path"], []) + [item]

    # Associer les fichiers chargés aux réunions
    historical_data: dict[str, list[dict]] = {}
    for meeting_title, history_entries in historical_index_entries.items():
        items = []
        for entry in history_entries:
            items.extend(loaded_by_path.get(entry["path"], []))
        historical_data[meeting_title] = items

    # ═══ Génération du briefing avec Claude ═══
    briefing = generate_briefing_with_claude(target_date, meetings_today, historical_data)

    # Affichage avec rich
    console.print(Rule(style="blue"))
    console.print(Panel(
        briefing,
        title=f"[bold]Briefing du matin — {target_date}[/bold]",
        border_style="blue",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    # Permettre de passer une date en argument
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(date_arg)
