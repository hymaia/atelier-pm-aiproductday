from __future__ import annotations
from pathlib import Path


def load(filepath: str | Path) -> list[dict]:
    """Lit un fichier message Slack .md et retourne une liste avec un dict normalisé."""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    headers, _, body = content.partition("---\n")

    meta = {}
    for line in headers.strip().splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            meta[key.strip().lower()] = value.strip()

    return [{
        "type": "slack",
        "filename": path.name,
        "from": meta.get("from", ""),
        "to": None,
        "subject": f"[Slack #{meta.get('channel', '?')}] {meta.get('from', '')}",
        "date": meta.get("timestamp", ""),
        "channel": meta.get("channel", ""),
        "body": body.strip(),
    }]
