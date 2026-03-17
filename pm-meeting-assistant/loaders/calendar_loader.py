"""
calendar_loader.py — Charge les fichiers de calendrier (.ics et .csv).

Format de sortie normalisé :
{
    "date": "2026-03-17",
    "title": "Sync produit Acme",
    "participants": ["Alice", "Bob"],
    "start_time": "09:00",
    "end_time": "09:45",
    "location": "Zoom",
    "decisions": "",
    "actions": "",
    "raw_text": "..."
}
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from datetime import datetime


def _parse_ics(filepath: Path) -> list[dict]:
    """Parse un fichier .ics (iCalendar) et retourne les événements."""
    events = []
    try:
        from icalendar import Calendar
        with open(filepath, "rb") as f:
            cal = Calendar.from_ical(f.read())
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get("DTSTART")
                date_str = ""
                time_str = ""
                if dtstart:
                    dt = dtstart.dt
                    if hasattr(dt, "strftime"):
                        date_str = dt.strftime("%Y-%m-%d")
                        time_str = dt.strftime("%H:%M") if hasattr(dt, "hour") else ""

                summary = str(component.get("SUMMARY", ""))
                description = str(component.get("DESCRIPTION", ""))
                location = str(component.get("LOCATION", ""))
                attendees_raw = component.get("ATTENDEE", [])

                # Normaliser la liste des participants
                if not isinstance(attendees_raw, list):
                    attendees_raw = [attendees_raw]
                participants = []
                for a in attendees_raw:
                    name = str(a)
                    # Extraire le nom depuis mailto: ou CN=
                    cn_match = re.search(r"CN=([^;:]+)", name)
                    if cn_match:
                        participants.append(cn_match.group(1).strip())
                    else:
                        participants.append(name.replace("mailto:", "").strip())

                raw_text = f"{date_str} {time_str}\n{summary}\n{description}\nParticipants: {', '.join(participants)}"

                events.append({
                    "date": date_str,
                    "title": summary,
                    "participants": participants,
                    "start_time": time_str,
                    "end_time": "",
                    "location": location,
                    "decisions": "",
                    "actions": "",
                    "raw_text": raw_text,
                })
    except ImportError:
        # Si icalendar n'est pas installé, tenter un parsing basique
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            events.append({
                "date": "",
                "title": filepath.stem,
                "participants": [],
                "start_time": "",
                "end_time": "",
                "location": "",
                "decisions": "",
                "actions": "",
                "raw_text": content[:2000],
            })
        except Exception:
            pass
    except Exception as e:
        print(f"  ⚠ Erreur lecture ICS {filepath.name}: {e}")

    return events


def _parse_csv(filepath: Path) -> list[dict]:
    """Parse un fichier .csv d'agenda."""
    events = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normaliser les noms de colonnes (minuscules, sans espaces)
                row_norm = {k.lower().strip(): v.strip() for k, v in row.items() if k}

                date = row_norm.get("date", "")
                start_time = row_norm.get("start_time", row_norm.get("heure_debut", row_norm.get("start", "")))
                end_time = row_norm.get("end_time", row_norm.get("heure_fin", row_norm.get("end", "")))
                title = row_norm.get("title", row_norm.get("titre", row_norm.get("subject", row_norm.get("sujet", ""))))
                location = row_norm.get("location", row_norm.get("lieu", ""))
                description = row_norm.get("description", "")

                # Participants : peut être séparé par ; ou ,
                participants_raw = row_norm.get("participants", "")
                participants = [p.strip() for p in re.split(r"[;|]", participants_raw) if p.strip()]

                raw_text = f"{date} {start_time}-{end_time}\n{title}\n{description}\nLieu: {location}\nParticipants: {', '.join(participants)}"

                events.append({
                    "date": date,
                    "title": title,
                    "participants": participants,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": location,
                    "decisions": "",
                    "actions": "",
                    "raw_text": raw_text,
                })
    except Exception as e:
        print(f"  ⚠ Erreur lecture CSV calendrier {filepath.name}: {e}")

    return events


def load(filepath: str | Path) -> list[dict]:
    """
    Charge un fichier calendrier et retourne une liste d'événements normalisés.

    Args:
        filepath: Chemin vers le fichier (.ics ou .csv)

    Returns:
        Liste de dicts normalisés avec date, title, participants, etc.
    """
    path = Path(filepath)
    if not path.exists():
        return []

    if path.suffix == ".ics":
        return _parse_ics(path)
    elif path.suffix == ".csv":
        return _parse_csv(path)
    else:
        return []
