#!/usr/bin/env python3
"""
Récupère les données de briefing pour une date donnée.
Glob direct sur data/ — pas d'index requis.
Appelé par SKILL.md via : !`python3 "${CLAUDE_SKILL_DIR}/fetch_agenda.py" $ARGUMENTS`
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

SKILL_DIR = Path(__file__).parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

sys.path.insert(0, str(PROJECT_ROOT))


def load_file(filepath: Path):
    """Charge un fichier via le bon loader selon son dossier parent."""
    parent = filepath.parent.name
    try:
        if parent == "transcripts":
            from utils.transcript_loader import load
        elif parent == "notes":
            from utils.notes_loader import load
        elif parent == "summaries":
            from utils.summary_loader import load
        else:
            return []
        return load(str(filepath))
    except Exception as e:
        return [{"raw_text": f"[Erreur chargement {filepath.name} : {e}]"}]


def extract_client(participants: list[str]) -> str:
    """Extrait le nom du client depuis les participants via le pattern 'Nom (Société)'."""
    import re
    for p in participants:
        match = re.search(r"\(([^)]+)\)", p)
        if match:
            return match.group(1).strip()
    return ""


def find_client_files(client: str) -> list[Path]:
    """Trouve tous les fichiers historiques correspondant au client."""
    if not client:
        return []
    keyword = client.lower().split()[0]  # "Acme Corp" → "acme"
    files = []
    for folder in ["transcripts", "notes", "summaries"]:
        folder_path = DATA_DIR / folder
        if folder_path.exists():
            files.extend([f for f in folder_path.iterdir() if keyword in f.name.lower()])
    return sorted(files, key=lambda f: f.name, reverse=True)


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())

    # Étape 1 : charger le calendrier du jour
    from utils.calendar_loader import load as load_calendar

    calendar_dir = DATA_DIR / "calendar"
    if not calendar_dir.exists():
        print("AUCUNE DONNÉE : dossier data/calendar/ introuvable.")
        sys.exit(0)

    meetings = []
    for f in calendar_dir.glob("*.csv"):
        meetings.extend(load_calendar(str(f)))

    day_meetings = [m for m in meetings if m.get("date") == target_date]

    if not day_meetings:
        print(f"AUCUNE RÉUNION trouvée pour le {target_date}.")
        sys.exit(0)

    print(f"DATE : {target_date}")
    print(f"RÉUNIONS DU JOUR : {len(day_meetings)}")
    print()

    # Étape 2 : pour chaque réunion, chercher l'historique par client
    for meeting in sorted(day_meetings, key=lambda m: m.get("start_time", "")):
        print(f"=== RÉUNION : {meeting.get('title', 'Sans titre')} ===")
        print(f"Heure       : {meeting.get('start_time', '?')} - {meeting.get('end_time', '?')}")
        print(f"Lieu/Format : {meeting.get('location', 'Non précisé')}")
        print(f"Durée       : {meeting.get('duration_min', '?')} min")
        print(f"Participants: {', '.join(meeting.get('participants', []))}")
        print()

        client = extract_client(meeting.get("participants", []))
        historical_files = find_client_files(client)

        if not historical_files:
            print(f"HISTORIQUE : Aucun fichier trouvé pour '{client}'.")
            print()
            continue

        print(f"HISTORIQUE ({len(historical_files)} fichier(s)) :")
        for filepath in historical_files:
            items = load_file(filepath)
            for item in items:
                print(f"--- {item.get('date', '?')} : {item.get('title', filepath.stem)} ---")
                if item.get("decisions"):
                    print(f"Décisions  : {item['decisions']}")
                if item.get("actions"):
                    print(f"Actions    : {item['actions']}")
                if item.get("raw_text"):
                    text = item["raw_text"][:2000]
                    if len(item["raw_text"]) > 2000:
                        text += "\n...[tronqué]"
                    print(f"Contenu    :\n{text}")
                print()

        print()


if __name__ == "__main__":
    main()
