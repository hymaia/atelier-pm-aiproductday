from __future__ import annotations
from pathlib import Path


def load(filepath: Path) -> dict:
    """
    Lit un fichier source et retourne ses métadonnées + contenu brut.

    Returns:
        dict avec les clés :
          - filename (str) : nom du fichier
          - language (str) : langage détecté depuis l'extension
          - content (str) : contenu brut du fichier
    """
    ext_to_language = {
        ".py": "Python",
        ".ts": "TypeScript",
        ".js": "JavaScript",
        ".go": "Go",
        ".java": "Java",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
    }
    ext = filepath.suffix.lower()
    language = ext_to_language.get(ext, ext.lstrip(".").upper() or "Unknown")

    return {
        "filename": filepath.name,
        "language": language,
        "content": filepath.read_text(encoding="utf-8"),
    }
