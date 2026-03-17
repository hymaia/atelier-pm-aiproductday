"""
summary_loader.py — Charge les comptes-rendus structurés (.csv).

Format attendu du CSV :
    date, participants, title, decisions, actions, status

Format de sortie normalisé :
{
    "date": "2026-03-10",
    "title": "Sync produit Acme",
    "participants": ["Alice Martin", "Bob Leroy"],
    "decisions": "...",
    "actions": "...",
    "raw_text": "..."
}
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


def load(filepath: str | Path) -> list[dict]:
    """
    Charge un fichier CSV de comptes-rendus et retourne une liste normalisée.

    Chaque ligne du CSV devient un enregistrement.

    Args:
        filepath: Chemin vers le fichier .csv

    Returns:
        Liste de dicts normalisés, une entrée par ligne de données
    """
    path = Path(filepath)
    if not path.exists():
        return []

    results = []

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Normaliser les clés (minuscules, sans espaces)
                row_norm = {k.lower().strip(): v.strip() if v else "" for k, v in row.items() if k}

                # Extraire les champs
                date = _get_field(row_norm, ["date"])
                if date:
                    # S'assurer que c'est au format ISO
                    m = re.search(r"\d{4}-\d{2}-\d{2}", date)
                    date = m.group(0) if m else date

                title = _get_field(row_norm, ["title", "titre", "sujet", "subject"])
                participants_raw = _get_field(row_norm, ["participants", "participant"])
                decisions = _get_field(row_norm, ["decisions", "décisions", "decision"])
                actions = _get_field(row_norm, ["actions", "action", "tâches", "tasks"])

                # Parser les participants
                participants = []
                if participants_raw:
                    participants = [p.strip() for p in re.split(r"[;|]", participants_raw) if p.strip()]

                # Construire le texte brut pour la recherche
                raw_parts = []
                if date:
                    raw_parts.append(f"Date: {date}")
                if title:
                    raw_parts.append(f"Titre: {title}")
                if participants_raw:
                    raw_parts.append(f"Participants: {participants_raw}")
                if decisions:
                    raw_parts.append(f"Décisions: {decisions}")
                if actions:
                    raw_parts.append(f"Actions: {actions}")
                raw_text = "\n".join(raw_parts)

                # Filtrer les lignes vides
                if not title and not decisions and not actions:
                    continue

                results.append({
                    "date": date,
                    "title": title,
                    "participants": participants,
                    "decisions": decisions,
                    "actions": actions,
                    "raw_text": raw_text,
                })

    except Exception as e:
        print(f"  ⚠ Erreur lecture CSV summary {path.name}: {e}")

    return results


def _get_field(row: dict, keys: list[str]) -> str:
    """Retourne la valeur du premier champ correspondant dans le dict."""
    for key in keys:
        if key in row and row[key]:
            return row[key]
    return ""


def get_open_actions(entries: list[dict]) -> list[dict]:
    """
    Filtre et retourne uniquement les actions non résolues.

    Cherche le pattern [OPEN] dans les champs actions.
    """
    open_items = []
    for entry in entries:
        actions_text = entry.get("actions", "")
        if not actions_text:
            continue

        # Trouver les actions avec [OPEN]
        open_actions = []
        for line in actions_text.splitlines():
            if "[OPEN]" in line.upper() or "OPEN" in line.upper():
                # Nettoyer le tag du status
                clean = re.sub(r"\[OPEN\]\s*", "", line, flags=re.IGNORECASE).strip()
                if clean:
                    open_actions.append(clean)

        if open_actions:
            open_items.append({
                "date": entry.get("date"),
                "title": entry.get("title"),
                "actions": open_actions,
            })

    return open_items
