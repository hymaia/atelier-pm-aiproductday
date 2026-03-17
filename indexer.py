"""
indexer.py — Maintient index.json à jour avec les métadonnées de tous les fichiers dans /data.

Principe : extraire les métadonnées (date, client, participants, titre) sans lire
le contenu complet des fichiers. L'index est léger et rapide à charger.

Usage :
    python indexer.py          → indexe les nouveaux fichiers
    python indexer.py --reset  → recrée l'index depuis zéro
"""

from __future__ import annotations

import json
import os
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path


# Chemin racine du projet
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = BASE_DIR / "index.json"

# Extensions supportées par type de dossier
SUPPORTED_EXTENSIONS = {
    "calendar": [".csv", ".ics"],
    "transcripts": [".txt", ".json"],
    "notes": [".md", ".pdf", ".docx"],
    "summaries": [".csv"],
}

# Mois français → numéro pour parser les noms de fichiers style "14mars"
MOIS_FR = {
    "jan": "01", "janv": "01", "janvier": "01",
    "feb": "02", "fev": "02", "févr": "02", "fevrier": "02", "février": "02",
    "mar": "03", "mars": "03",
    "apr": "04", "avr": "04", "avril": "04",
    "may": "05", "mai": "05",
    "jun": "06", "juin": "06",
    "jul": "07", "juil": "07", "juillet": "07",
    "aug": "08", "aout": "08", "août": "08",
    "sep": "09", "sept": "09", "septembre": "09",
    "oct": "10", "octobre": "10",
    "nov": "11", "novembre": "11",
    "dec": "12", "déc": "12", "decembre": "12", "décembre": "12",
}


def generate_file_id(filepath: Path) -> str:
    """Génère un identifiant unique stable basé sur le chemin du fichier."""
    return hashlib.md5(str(filepath).encode()).hexdigest()[:12]


def detect_date_from_filename(filename: str) -> str | None:
    """
    Extrait une date depuis le nom de fichier.
    Patterns supportés : YYYY-MM-DD, DDMMYYYY, DDmois (ex: 14mars), DDmoisYYYY
    """
    stem = Path(filename).stem

    # Pattern ISO : YYYY-MM-DD
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", stem)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    # Pattern DDmoisYYYY ou DDmois (ex: 14mars2026 ou 14mars)
    match = re.search(r"(\d{1,2})(jan|janv|janvier|feb|fev|févr|fevrier|février|mar|mars|apr|avr|avril|may|mai|jun|juin|jul|juil|juillet|aug|aout|août|sep|sept|septembre|oct|octobre|nov|novembre|dec|déc|decembre|décembre)(\d{4})?", stem, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month = MOIS_FR.get(match.group(2).lower(), "01")
        year = match.group(3) or datetime.now().strftime("%Y")
        return f"{year}-{month}-{day}"

    # Pattern DDMMYYYY
    match = re.search(r"(\d{2})(\d{2})(\d{4})", stem)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"

    return None


def detect_client_from_filename(filename: str) -> str | None:
    """
    Extrait le nom du client depuis le nom de fichier.
    Pattern attendu : client_date ou client_description_date
    """
    stem = Path(filename).stem
    # Enlever les dates du stem pour isoler le client
    clean = re.sub(r"\d{4}-\d{2}-\d{2}", "", stem)
    clean = re.sub(r"\d{1,2}(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\d*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\d+", "", clean)
    # Prendre le premier segment avant _ ou -
    parts = re.split(r"[_\-]", clean)
    parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 1]
    if parts:
        return parts[0].capitalize()
    return None


def read_first_lines(filepath: Path, n: int = 5) -> list[str]:
    """Lit les n premières lignes d'un fichier texte de manière safe."""
    lines = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line.strip())
    except Exception:
        pass
    return lines


def extract_metadata_calendar(filepath: Path) -> dict:
    """Extrait les métadonnées d'un fichier calendrier (.csv ou .ics)."""
    lines = read_first_lines(filepath, 10)
    date = detect_date_from_filename(filepath.name)
    participants = []
    title = detect_client_from_filename(filepath.name) or "Calendrier"

    if filepath.suffix == ".csv" and len(lines) > 1:
        # Parser le header CSV pour trouver les colonnes
        header = lines[0].split(",") if lines else []
        header_lower = [h.lower().strip() for h in header]
        # Chercher des dates dans les données
        for line in lines[1:]:
            if line:
                cols = line.split(",")
                # Chercher une date dans la première colonne
                if cols and not date:
                    date = detect_date_from_filename(cols[0])
                # Chercher des participants
                for i, h in enumerate(header_lower):
                    if "participant" in h and i < len(cols):
                        parts = re.split(r"[;|]", cols[i])
                        participants.extend([p.strip() for p in parts if p.strip()])
                break

    return {
        "date": date,
        "client": detect_client_from_filename(filepath.name),
        "participants": list(set(participants))[:5],
        "title": title,
    }


def extract_metadata_transcript(filepath: Path) -> dict:
    """Extrait les métadonnées d'une transcription (.txt ou .json)."""
    lines = read_first_lines(filepath, 8)
    date = detect_date_from_filename(filepath.name)
    participants = []
    title = None
    client = detect_client_from_filename(filepath.name)

    if filepath.suffix == ".json":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            date = date or data.get("date")
            title = data.get("title") or data.get("subject")
            participants = data.get("participants", [])
            client = client or data.get("client")
        except Exception:
            pass
    else:
        # Parser les premières lignes pour date, titre, participants
        for line in lines:
            if not date:
                m = re.search(r"\d{4}-\d{2}-\d{2}", line)
                if m:
                    date = m.group(0)

            if not title and re.match(r"^[Tt]itre\s*:", line):
                title = re.sub(r"^[Tt]itre\s*:\s*", "", line).strip()

            if re.match(r"^[Pp]articipants?\s*:", line):
                parts_str = re.sub(r"^[Pp]articipants?\s*:\s*", "", line)
                participants = [p.strip() for p in re.split(r"[,;]", parts_str) if p.strip()]

    title = title or filepath.stem.replace("_", " ").title()
    return {
        "date": date,
        "client": client,
        "participants": participants[:8],
        "title": title,
    }


def extract_metadata_notes(filepath: Path) -> dict:
    """Extrait les métadonnées de notes de réunion (.md, .pdf, .docx)."""
    date = detect_date_from_filename(filepath.name)
    participants = []
    title = None
    client = detect_client_from_filename(filepath.name)

    if filepath.suffix == ".md":
        lines = read_first_lines(filepath, 10)
        for line in lines:
            # Titre depuis heading Markdown
            if not title and line.startswith("# "):
                title = line[2:].strip()

            # Date dans les metadata
            if not date:
                m = re.search(r"\d{4}-\d{2}-\d{2}", line)
                if m:
                    date = m.group(0)
                else:
                    m = re.search(r"(\d{1,2})\s+(jan|feb|mar|avr|mai|juin|juil|août|aout|sep|oct|nov|déc|dec)\w*\s+(\d{4})", line, re.IGNORECASE)
                    if m:
                        day = m.group(1).zfill(2)
                        month = MOIS_FR.get(m.group(2).lower()[:3], "01")
                        year = m.group(3)
                        date = f"{year}-{month}-{day}"

            # Participants
            if "participant" in line.lower() and ":" in line:
                parts_str = line.split(":", 1)[-1]
                participants = [p.strip() for p in re.split(r"[,;]", parts_str) if p.strip()]

    title = title or filepath.stem.replace("_", " ").title()
    return {
        "date": date,
        "client": client,
        "participants": participants[:8],
        "title": title,
    }


def extract_metadata_summary(filepath: Path) -> dict:
    """Extrait les métadonnées d'un compte-rendu structuré (.csv)."""
    lines = read_first_lines(filepath, 3)
    date = detect_date_from_filename(filepath.name)
    participants = []
    title = None
    client = detect_client_from_filename(filepath.name)

    if len(lines) >= 2:
        header = [h.lower().strip() for h in lines[0].split(",")]
        data_line = lines[1]

        # Splitter en tenant compte des guillemets CSV
        import csv
        import io
        try:
            reader = csv.reader(io.StringIO(data_line))
            cols = next(reader)
        except Exception:
            cols = data_line.split(",")

        for i, h in enumerate(header):
            if i >= len(cols):
                break
            val = cols[i].strip().strip('"')
            if "date" in h and not date:
                date = detect_date_from_filename(val) or val[:10] if val else date
            elif "participant" in h:
                parts = re.split(r"[;|]", val)
                participants = [p.strip() for p in parts if p.strip()]
            elif "title" in h or "titre" in h:
                title = val

    title = title or filepath.stem.replace("_", " ").title()
    return {
        "date": date,
        "client": client,
        "participants": participants[:8],
        "title": title,
    }


FOLDER_TO_TYPE = {
    "calendar": "calendar",
    "transcripts": "transcript",
    "notes": "note",
    "summaries": "summary",
}


def get_file_type(filepath: Path) -> str | None:
    """Détermine le type d'un fichier depuis son dossier parent."""
    parts = filepath.relative_to(DATA_DIR).parts
    if not parts:
        return None
    folder = parts[0]
    if folder in SUPPORTED_EXTENSIONS:
        if filepath.suffix in SUPPORTED_EXTENSIONS[folder]:
            return FOLDER_TO_TYPE.get(folder)
    return None


def index_file(filepath: Path) -> dict | None:
    """
    Crée une entrée d'index pour un fichier.
    Retourne None si le fichier n'est pas supporté.
    """
    file_type = get_file_type(filepath)
    if not file_type:
        return None

    # Sélectionner le bon extracteur selon le type
    extractors = {
        "calendar": extract_metadata_calendar,
        "transcript": extract_metadata_transcript,
        "note": extract_metadata_notes,
        "summary": extract_metadata_summary,
    }

    extractor = extractors.get(file_type)
    if not extractor:
        return None

    meta = extractor(filepath)
    rel_path = str(filepath.relative_to(BASE_DIR))
    size_kb = round(filepath.stat().st_size / 1024, 1)

    return {
        "id": generate_file_id(filepath),
        "path": rel_path,
        "type": file_type,
        "date": meta.get("date"),
        "client": meta.get("client"),
        "participants": meta.get("participants", []),
        "title": meta.get("title"),
        "size_kb": size_kb,
        "indexed_at": datetime.now().isoformat(timespec="seconds"),
    }


def load_index() -> list[dict]:
    """Charge l'index existant depuis index.json."""
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_index(entries: list[dict]) -> None:
    """Sauvegarde l'index dans index.json."""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def scan_data_directory() -> list[Path]:
    """Scanne récursivement /data et retourne tous les fichiers supportés."""
    files = []
    if not DATA_DIR.exists():
        return files
    for folder, extensions in SUPPORTED_EXTENSIONS.items():
        folder_path = DATA_DIR / folder
        if not folder_path.exists():
            continue
        for ext in extensions:
            files.extend(folder_path.glob(f"*{ext}"))
    return sorted(files)


def run_indexer(reset: bool = False) -> tuple[int, int]:
    """
    Lance l'indexation.

    Returns:
        (nouveaux, déjà_connus) : nombre de fichiers indexés et déjà présents
    """
    existing = [] if reset else load_index()
    existing_ids = {entry["id"] for entry in existing}

    all_files = scan_data_directory()
    new_entries = []
    already_known = 0

    for filepath in all_files:
        file_id = generate_file_id(filepath)
        if file_id in existing_ids:
            already_known += 1
            continue

        entry = index_file(filepath)
        if entry:
            new_entries.append(entry)

    updated_index = existing + new_entries
    save_index(updated_index)

    return len(new_entries), already_known


if __name__ == "__main__":
    reset_mode = "--reset" in sys.argv

    if reset_mode:
        print("Mode reset : reconstruction de l'index depuis zéro...")

    nouveaux, deja_connus = run_indexer(reset=reset_mode)

    print(f"\n✓ Indexation terminée")
    print(f"  → {nouveaux} nouveau(x) fichier(s) indexé(s)")
    if not reset_mode:
        print(f"  → {deja_connus} fichier(s) déjà connu(s)")

    # Afficher un aperçu de l'index
    index = load_index()
    print(f"\n📁 Index total : {len(index)} fichier(s)")
    for entry in sorted(index, key=lambda x: (x.get("date") or "", x.get("type") or "")):
        date_str = entry.get("date") or "date inconnue"
        client_str = entry.get("client") or "client inconnu"
        print(f"  [{entry['type']:10s}] {date_str} | {client_str:20s} | {entry['title']}")
