"""
notes_loader.py — Charge les notes de réunion (.md, .pdf, .docx).

Format de sortie normalisé :
{
    "date": "2026-03-01",
    "title": "Notes Carrefour Digital",
    "participants": ["Alice Martin", "Marc Dupont"],
    "decisions": "...",
    "actions": "...",
    "raw_text": "..."
}
"""

from __future__ import annotations

import re
from pathlib import Path


def _parse_markdown(filepath: Path) -> dict:
    """Parse un fichier Markdown (.md)."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠ Erreur lecture MD {filepath.name}: {e}")
        return {}

    lines = content.splitlines()
    date = None
    title = None
    participants = []
    decisions = []
    actions = []

    # États pour parser les sections
    current_section = None

    for line in lines:
        stripped = line.strip()

        # Titre principal (H1)
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()

        # Date dans les métadonnées en bold ou plaintext
        if not date:
            m = re.search(r"\*\*[Dd]ate\s*:\*\*\s*(.+)", stripped)
            if m:
                raw_date = m.group(1).strip()
                iso_match = re.search(r"\d{4}-\d{2}-\d{2}", raw_date)
                if iso_match:
                    date = iso_match.group(0)
                else:
                    # Format "1er mars 2026"
                    month_map = {
                        "janvier": "01", "février": "02", "fevrier": "02",
                        "mars": "03", "avril": "04", "mai": "05", "juin": "06",
                        "juillet": "07", "août": "08", "aout": "08",
                        "septembre": "09", "octobre": "10", "novembre": "11",
                        "décembre": "12", "decembre": "12",
                    }
                    dm = re.search(r"(\d{1,2})\w*\s+(\w+)\s+(\d{4})", raw_date)
                    if dm:
                        mois = month_map.get(dm.group(2).lower())
                        if mois:
                            date = f"{dm.group(3)}-{mois}-{dm.group(1).zfill(2)}"

        # Participants
        if not participants:
            m = re.search(r"\*\*[Pp]articipants?\s*:\*\*\s*(.+)", stripped)
            if m:
                parts_str = m.group(1).strip()
                participants = [p.strip() for p in re.split(r"[,;]", parts_str) if p.strip()]

        # Détection de sections
        if re.match(r"^#{1,3}\s+(Décisions?|Décision|Decisions?)", stripped, re.IGNORECASE):
            current_section = "decisions"
            continue
        elif re.match(r"^#{1,3}\s+(Actions?|Tâches?|TODO)", stripped, re.IGNORECASE):
            current_section = "actions"
            continue
        elif stripped.startswith("#"):
            current_section = None

        # Collecter le contenu des sections
        if current_section == "decisions" and stripped and not stripped.startswith("#"):
            if stripped.startswith(("- ", "* ", "• ")):
                decisions.append(stripped[2:].strip())
            elif re.match(r"^\d+\.\s", stripped):
                decisions.append(re.sub(r"^\d+\.\s*", "", stripped))

        if current_section == "actions" and stripped and not stripped.startswith("#"):
            # Items de checklist Markdown : - [ ] ou - [x]
            m = re.match(r"^-\s+\[([xX ]?)\]\s+(.+)", stripped)
            if m:
                status = "DONE" if m.group(1).lower() == "x" else "OPEN"
                actions.append(f"[{status}] {m.group(2).strip()}")
            elif stripped.startswith(("- ", "* ", "• ")):
                actions.append(stripped[2:].strip())

    title = title or filepath.stem.replace("_", " ").title()

    return {
        "date": date,
        "title": title,
        "participants": participants,
        "decisions": "\n".join(decisions),
        "actions": "\n".join(actions),
        "raw_text": content,
    }


def _parse_pdf(filepath: Path) -> dict:
    """Parse un fichier PDF avec pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages[:5]:  # Limiter aux 5 premières pages
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        content = "\n".join(text_parts)
    except ImportError:
        print("  ⚠ pdfplumber non installé. Installer avec : pip install pdfplumber")
        return {"title": filepath.stem, "raw_text": f"[PDF non lisible : {filepath.name}]"}
    except Exception as e:
        print(f"  ⚠ Erreur lecture PDF {filepath.name}: {e}")
        return {}

    if not content:
        return {"title": filepath.stem, "raw_text": ""}

    # Extraire date et participants depuis le texte brut
    date = None
    m = re.search(r"\d{4}-\d{2}-\d{2}", content)
    if m:
        date = m.group(0)

    participants = []
    m = re.search(r"[Pp]articipants?\s*:\s*(.+)", content)
    if m:
        participants = [p.strip() for p in re.split(r"[,;]", m.group(1)) if p.strip()][:8]

    # Titre : première ligne non vide
    title = None
    for line in content.splitlines():
        if line.strip():
            title = line.strip()[:100]
            break
    title = title or filepath.stem

    return {
        "date": date,
        "title": title,
        "participants": participants,
        "decisions": "",
        "actions": "",
        "raw_text": content,
    }


def _parse_docx(filepath: Path) -> dict:
    """Parse un fichier Word (.docx)."""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = "\n".join(paragraphs)
    except ImportError:
        print("  ⚠ python-docx non installé. Installer avec : pip install python-docx")
        return {"title": filepath.stem, "raw_text": f"[DOCX non lisible : {filepath.name}]"}
    except Exception as e:
        print(f"  ⚠ Erreur lecture DOCX {filepath.name}: {e}")
        return {}

    if not content:
        return {"title": filepath.stem, "raw_text": ""}

    # Extraire les métadonnées du contenu
    date = None
    m = re.search(r"\d{4}-\d{2}-\d{2}", content)
    if m:
        date = m.group(0)

    participants = []
    m = re.search(r"[Pp]articipants?\s*:\s*(.+)", content)
    if m:
        participants = [p.strip() for p in re.split(r"[,;]", m.group(1)) if p.strip()][:8]

    title = paragraphs[0][:100] if paragraphs else filepath.stem

    return {
        "date": date,
        "title": title,
        "participants": participants,
        "decisions": "",
        "actions": "",
        "raw_text": content,
    }


def load(filepath: str | Path) -> list[dict]:
    """
    Charge un fichier de notes et retourne une liste normalisée.

    Args:
        filepath: Chemin vers le fichier (.md, .pdf, ou .docx)

    Returns:
        Liste de dicts normalisés (généralement un seul élément)
    """
    path = Path(filepath)
    if not path.exists():
        return []

    parsers = {
        ".md": _parse_markdown,
        ".pdf": _parse_pdf,
        ".docx": _parse_docx,
    }

    parser = parsers.get(path.suffix)
    if not parser:
        return []

    result = parser(path)
    return [result] if result else []
