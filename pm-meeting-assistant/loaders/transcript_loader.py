"""
transcript_loader.py — Charge les transcriptions de réunions (.txt et .json).

Format de sortie normalisé :
{
    "date": "2026-03-10",
    "title": "Sync produit Acme",
    "participants": ["Alice Martin", "Bob Leroy"],
    "decisions": "",
    "actions": "",
    "raw_text": "..."  # contenu brut pour recherche et génération
}
"""

from __future__ import annotations

import json
import re
from pathlib import Path


def _extract_from_txt(filepath: Path) -> dict:
    """Parse un fichier .txt de transcription."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠ Erreur lecture TXT {filepath.name}: {e}")
        return {}

    lines = content.splitlines()
    date = None
    title = None
    participants = []

    # Analyser les premières lignes pour les métadonnées structurées
    for line in lines[:15]:
        stripped = line.strip()

        # Date
        if not date:
            m = re.search(r"\d{4}-\d{2}-\d{2}", stripped)
            if m:
                date = m.group(0)
            # Pattern "1er mars 2026" ou "17 mars 2026"
            if not date:
                m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", stripped)
                if m:
                    mois_map = {
                        "janvier": "01", "février": "02", "fevrier": "02",
                        "mars": "03", "avril": "04", "mai": "05", "juin": "06",
                        "juillet": "07", "août": "08", "aout": "08",
                        "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12", "decembre": "12",
                    }
                    mois = mois_map.get(m.group(2).lower())
                    if mois:
                        date = f"{m.group(3)}-{mois}-{m.group(1).zfill(2)}"

        # Titre
        if not title and re.match(r"^[Tt]itre\s*:", stripped):
            title = re.sub(r"^[Tt]itre\s*:\s*", "", stripped).strip()

        # Participants
        if re.match(r"^[Pp]articipants?\s*:", stripped):
            parts_str = re.sub(r"^[Pp]articipants?\s*:\s*", "", stripped)
            participants = [p.strip() for p in re.split(r"[,;]", parts_str) if p.strip()]

    title = title or filepath.stem.replace("_", " ").title()

    return {
        "date": date,
        "title": title,
        "participants": participants,
        "decisions": "",
        "actions": _extract_actions_from_text(content),
        "raw_text": content,
    }


def _extract_from_json(filepath: Path) -> dict:
    """Parse un fichier .json de transcription."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ⚠ Erreur lecture JSON {filepath.name}: {e}")
        return {}

    # Gérer plusieurs formats JSON possibles
    date = data.get("date") or data.get("meeting_date") or data.get("timestamp", "")[:10]
    title = data.get("title") or data.get("subject") or data.get("topic") or filepath.stem.replace("_", " ").title()
    participants = data.get("participants") or data.get("attendees") or []

    # Si participants est une liste de dicts, extraire les noms
    if participants and isinstance(participants[0], dict):
        participants = [p.get("name") or p.get("speaker") or str(p) for p in participants]

    # Le contenu brut peut être dans différents champs
    raw_text = data.get("transcript") or data.get("text") or data.get("content") or json.dumps(data, ensure_ascii=False)

    return {
        "date": date,
        "title": title,
        "participants": participants,
        "decisions": data.get("decisions", ""),
        "actions": data.get("actions", "") or _extract_actions_from_text(raw_text),
        "raw_text": raw_text,
    }


def _extract_actions_from_text(text: str) -> str:
    """
    Tente d'extraire les actions/tâches depuis un texte de transcription.
    Cherche des patterns comme "Actions :", "TODO:", "[x]", etc.
    """
    actions = []
    lines = text.splitlines()
    in_actions_section = False

    for line in lines:
        stripped = line.strip()

        # Détecter une section "Actions"
        if re.match(r"^[Aa]ctions?\s*(pour\s+la\s+semaine)?\s*:", stripped):
            in_actions_section = True
            continue

        # Sortir de la section actions si on arrive à une nouvelle section
        if in_actions_section and re.match(r"^#+\s+\w", stripped):
            in_actions_section = False

        # Collecter les items dans la section actions
        if in_actions_section and stripped and not stripped.startswith("["):
            actions.append(stripped)

        # Patterns directs d'actions en dehors de sections
        if re.match(r"^[-•]\s+\[?\]?\s*\w", stripped) and in_actions_section:
            actions.append(stripped)

    return "\n".join(actions[:10]) if actions else ""


def load(filepath: str | Path) -> list[dict]:
    """
    Charge un fichier de transcription et retourne une liste normalisée.

    Args:
        filepath: Chemin vers le fichier (.txt ou .json)

    Returns:
        Liste de dicts normalisés (généralement un seul élément par fichier)
    """
    path = Path(filepath)
    if not path.exists():
        return []

    if path.suffix == ".txt":
        result = _extract_from_txt(path)
    elif path.suffix == ".json":
        result = _extract_from_json(path)
    else:
        return []

    if not result:
        return []

    return [result]
