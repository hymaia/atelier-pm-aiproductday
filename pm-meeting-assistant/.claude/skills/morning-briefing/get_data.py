#!/usr/bin/env python3
"""
Récupère les données de briefing depuis index.json et charge les fichiers pertinents.
Appelé par SKILL.md via : !`python3 ${CLAUDE_SKILL_DIR}/get_data.py [YYYY-MM-DD]`
"""
from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import date

# .claude/skills/morning-briefing/ → remonter 3 niveaux → pm-meeting-assistant/
SKILL_DIR = Path(__file__).parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent


def load_file(entry: dict):
    """Charge un fichier via le bon loader selon son type."""
    sys.path.insert(0, str(PROJECT_ROOT))
    filepath = PROJECT_ROOT / entry["path"]
    if not filepath.exists():
        return []
    t = entry.get("type")
    try:
        if t == "transcript":
            from loaders.transcript_loader import load
        elif t == "notes":
            from loaders.notes_loader import load
        elif t == "summary":
            from loaders.summary_loader import load
        else:
            return []
        return load(str(filepath))
    except Exception as e:
        return [{"raw_text": f"[Erreur chargement : {e}]", "date": entry.get("date", ""), "title": entry.get("title", "")}]


def find_historical(index: list[dict], client: str, participants: list[str], target_date: str) -> list[dict]:
    """Trouve les fichiers historiques liés à un client/participants."""
    results = []
    for entry in index:
        if entry.get("type") == "calendar" or entry.get("date") == target_date:
            continue
        entry_client = entry.get("client", "").lower()
        entry_participants = [p.lower() for p in entry.get("participants", [])]
        match = False
        if client and client.lower() in entry_client:
            match = True
        for p in participants:
            p_lower = p.lower()
            if any(p_lower in ep for ep in entry_participants):
                match = True
                break
        if match:
            results.append(entry)
    results.sort(key=lambda e: e.get("date", ""), reverse=True)
    return results[:3]


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())

    # Vérification index
    index_path = PROJECT_ROOT / "index.json"
    if not index_path.exists():
        print("AUCUNE DONNÉE : index.json introuvable.")
        print("Exécutez d'abord : python3 indexer.py")
        sys.exit(0)

    with open(index_path) as f:
        index = json.load(f)

    # Étape 1 : réunions du jour depuis le calendrier
    sys.path.insert(0, str(PROJECT_ROOT))
    from loaders.calendar_loader import load as load_calendar

    calendar_entries = [e for e in index if e.get("type") == "calendar"]
    meetings = []
    for entry in calendar_entries:
        filepath = PROJECT_ROOT / entry["path"]
        if filepath.exists():
            meetings.extend(load_calendar(str(filepath)))

    day_meetings = [m for m in meetings if m.get("date") == target_date]

    if not day_meetings:
        print(f"AUCUNE RÉUNION trouvée pour le {target_date}.")
        print(f"Fichiers calendrier consultés : {len(calendar_entries)}")
        sys.exit(0)

    print(f"DATE : {target_date}")
    print(f"RÉUNIONS DU JOUR : {len(day_meetings)}")
    print()

    # Étape 2 : pour chaque réunion, charger l'historique
    for meeting in sorted(day_meetings, key=lambda m: m.get("start_time", "")):
        print(f"=== RÉUNION : {meeting.get('title', 'Sans titre')} ===")
        print(f"Heure       : {meeting.get('start_time', '?')} - {meeting.get('end_time', '?')}")
        print(f"Lieu/Format : {meeting.get('location', 'Non précisé')}")
        print(f"Durée       : {meeting.get('duration_min', '?')} min")
        print(f"Participants: {', '.join(meeting.get('participants', []))}")
        print()

        client = meeting.get("client", "")
        participants = meeting.get("participants", [])
        historical = find_historical(index, client, participants, target_date)

        if historical:
            print(f"HISTORIQUE ({len(historical)} fichier(s)) :")
            for h in historical:
                items = load_file(h)
                for item in items:
                    print(f"--- {item.get('date', h.get('date', '?'))} : {item.get('title', h.get('title', '?'))} ---")
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
        else:
            print("HISTORIQUE : Aucun historique trouvé pour ce client/ces participants.")

        print()


if __name__ == "__main__":
    main()
