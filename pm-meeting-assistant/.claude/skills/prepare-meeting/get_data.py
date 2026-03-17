#!/usr/bin/env python3
"""
Récupère les données de préparation de réunion depuis index.json.
Appelé par SKILL.md via : !`python3 ${CLAUDE_SKILL_DIR}/get_data.py <query>`
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

# .claude/skills/prepare-meeting/ → remonter 3 niveaux → pm-meeting-assistant/
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


def main():
    if len(sys.argv) < 2:
        print("ERREUR : Veuillez spécifier un nom de client ou de participant.")
        print("Usage : get_data.py <nom du client ou participant>")
        sys.exit(0)

    query = " ".join(sys.argv[1:]).lower().strip()

    # Vérification index
    index_path = PROJECT_ROOT / "index.json"
    if not index_path.exists():
        print("AUCUNE DONNÉE : index.json introuvable.")
        print("Exécutez d'abord : python3 indexer.py")
        sys.exit(0)

    with open(index_path) as f:
        index = json.load(f)

    # Filtrer les entrées non-calendrier correspondant à la query
    matches = []
    for entry in index:
        if entry.get("type") == "calendar":
            continue
        client = entry.get("client", "").lower()
        title = entry.get("title", "").lower()
        participants = [p.lower() for p in entry.get("participants", [])]
        path = entry.get("path", "").lower()

        if (query in client or query in title or
                any(query in p for p in participants) or
                query in path):
            matches.append(entry)

    if not matches:
        print(f"AUCUNE DONNÉE trouvée pour '{query}'.")
        print(f"Fichiers consultés : index.json — {len([e for e in index if e.get('type') != 'calendar'])} fichiers non-calendrier")
        sys.exit(0)

    # Trier par date décroissante, max 5
    matches.sort(key=lambda e: e.get("date", ""), reverse=True)
    matches = matches[:5]

    print(f"REQUÊTE : {query}")
    print(f"FICHIERS TROUVÉS : {len(matches)}")
    print()

    for entry in matches:
        items = load_file(entry)
        for item in items:
            print(f"=== {item.get('date', entry.get('date', '?'))} : {item.get('title', entry.get('title', '?'))} ===")
            print(f"Type        : {entry.get('type', '?')}")
            print(f"Participants: {', '.join(item.get('participants', entry.get('participants', [])))}")
            if item.get("decisions"):
                print(f"Décisions   : {item['decisions']}")
            if item.get("actions"):
                print(f"Actions     : {item['actions']}")
            if item.get("raw_text"):
                text = item["raw_text"][:2000]
                if len(item["raw_text"]) > 2000:
                    text += "\n...[tronqué]"
                print(f"Contenu     :\n{text}")
            print()


if __name__ == "__main__":
    main()
