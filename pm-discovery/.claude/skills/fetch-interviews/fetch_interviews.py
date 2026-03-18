from __future__ import annotations
import sys
from pathlib import Path

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.interview_loader import load

MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}

data_dir = project_dir / "data" / "interviews"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

# Convertir les noms de mois français en numéro pour matcher les dates
search_query = query
for mois, num in MOIS_FR.items():
    if mois in query:
        search_query = query.replace(mois, f"-{num}-")

interviews = []
for f in sorted(data_dir.glob("*.md")):
    interview = load(f)
    if not query:
        interviews.append(interview)
    else:
        searchable = " ".join([
            interview["persona"],
            interview["client"],
            interview["interviewer"],
            interview["date"],
            " ".join(interview["themes"]),
            interview["content"],
        ]).lower()
        if search_query in searchable or query in searchable:
            interviews.append(interview)

if not interviews:
    print(f"AUCUNE DONNÉE — aucune interview trouvée pour : '{query}'")
    sys.exit(0)

print(f"REQUÊTE : {query or 'toutes les interviews'}")
print(f"INTERVIEWS TROUVÉES : {len(interviews)}\n")

for iv in interviews:
    client_label = f" — {iv['client']}" if iv["client"] else " — Persona anonymisé"
    print(f"=== {iv['date']} : {iv['persona']}{client_label} ===")
    print(f"Intervieweur : {iv['interviewer']} | Durée : {iv['duration']}")
    print(f"Thèmes       : {', '.join(iv['themes'])}")
    print(f"Contenu :\n{iv['content']}")
    print()
