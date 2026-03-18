from __future__ import annotations
import csv
from pathlib import Path


def load(filepath: Path) -> list[dict]:
    """Lit un fichier CSV de tickets et retourne une liste de dicts normalisés."""
    tickets = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append({
                "id": row["id"].strip(),
                "title": row["title"].strip(),
                "type": row["type"].strip(),
                "status": row["status"].strip(),
                "priority": row["priority"].strip(),
                "assignee": row["assignee"].strip(),
                "sprint": row["sprint"].strip(),
                "created_at": row["created_at"].strip(),
                "labels": [l.strip() for l in row["labels"].split(";") if l.strip()],
            })
    return tickets
