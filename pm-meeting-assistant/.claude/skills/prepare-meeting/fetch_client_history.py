#!/usr/bin/env python3
"""
Récupère l'historique d'un client ou participant.
Glob direct sur data/ — pas d'index requis.
Appelé par SKILL.md via : !`python3 "${CLAUDE_SKILL_DIR}/fetch_client_history.py" $ARGUMENTS`
"""
from __future__ import annotations

import sys
from pathlib import Path

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


def main():
    if len(sys.argv) < 2:
        print("ERREUR : Veuillez spécifier un nom de client ou de participant.")
        print("Usage : fetch_client_history.py <nom du client>")
        sys.exit(0)

    query = " ".join(sys.argv[1:]).lower().strip()

    # Glob sur tous les dossiers de data sauf calendar
    matches = []
    for folder in ["transcripts", "notes", "summaries"]:
        folder_path = DATA_DIR / folder
        if folder_path.exists():
            matches.extend([f for f in folder_path.iterdir() if query in f.name.lower()])

    if not matches:
        print(f"AUCUNE DONNÉE trouvée pour '{query}'.")
        print(f"Dossiers consultés : data/transcripts/, data/notes/, data/summaries/")
        sys.exit(0)

    matches = sorted(matches, key=lambda f: f.name, reverse=True)

    print(f"REQUÊTE : {query}")
    print(f"FICHIERS TROUVÉS : {len(matches)}")
    print()

    for filepath in matches:
        items = load_file(filepath)
        for item in items:
            print(f"=== {item.get('date', '?')} : {item.get('title', filepath.stem)} ===")
            print(f"Type        : {filepath.parent.name}")
            print(f"Participants: {', '.join(item.get('participants', []))}")
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
