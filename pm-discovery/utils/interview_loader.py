from __future__ import annotations
from pathlib import Path


def load(filepath: Path) -> dict:
    """Lit un fichier .md d'interview et retourne un dict normalisé."""
    content = filepath.read_text(encoding="utf-8")

    metadata = {
        "date": "",
        "persona": "",
        "client": "",
        "interviewer": "",
        "duration": "",
        "themes": [],
    }

    # Extraire le frontmatter YAML
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip()
                    if key == "themes":
                        value = value.strip("[]").replace('"', "").replace("'", "")
                        metadata["themes"] = [t.strip() for t in value.split(",") if t.strip()]
                    elif key in metadata:
                        metadata[key] = value if value != "null" else ""
            body = parts[2].strip()
        else:
            body = content
    else:
        body = content

    return {
        "file": filepath.name,
        "date": metadata["date"],
        "persona": metadata["persona"],
        "client": metadata["client"],
        "interviewer": metadata["interviewer"],
        "duration": metadata["duration"],
        "themes": metadata["themes"],
        "content": body,
    }
