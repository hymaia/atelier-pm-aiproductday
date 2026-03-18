from __future__ import annotations
import re
from pathlib import Path


_VERSION_RE = re.compile(r"v(\d+\.\d+(?:\.\d+)?)", re.IGNORECASE)
_DATE_RE = re.compile(r"\*\*Date de release\*\*\s*:\s*(\S+)")


def load(filepath: Path) -> dict:
    """
    Lit un fichier changelog Markdown et retourne ses métadonnées + contenu brut.

    Returns:
        dict avec les clés :
          - filename (str) : nom du fichier
          - version (str) : numéro de version extrait (ex. "2.3.0")
          - date (str) : date de release extraite (ex. "2026-03-10"), ou ""
          - content (str) : contenu brut du fichier
    """
    content = filepath.read_text(encoding="utf-8")

    version_match = _VERSION_RE.search(filepath.name)
    version = version_match.group(1) if version_match else ""

    date_match = _DATE_RE.search(content)
    date = date_match.group(1) if date_match else ""

    return {
        "filename": filepath.name,
        "version": version,
        "date": date,
        "content": content,
    }
