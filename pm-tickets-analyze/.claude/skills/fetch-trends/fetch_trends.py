from __future__ import annotations
import sys
from pathlib import Path
from collections import Counter

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.ticket_loader import load

data_dir = project_dir / "data" / "tickets"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

# Charger tous les fichiers avec leur mois
files_data = {}
for f in sorted(data_dir.glob("*.csv")):
    month = f.stem.replace("tickets_", "")  # ex: "2026-03"
    files_data[month] = load(f)

if not files_data:
    print("AUCUNE DONNÉE — aucun fichier de tickets trouvé.")
    sys.exit(0)

print(f"FILTRE : {query or 'toutes périodes'}")
print(f"PÉRIODES ANALYSÉES : {', '.join(sorted(files_data.keys()))}\n")

for month in sorted(files_data.keys()):
    tickets = files_data[month]

    # Filtrer si query
    if query:
        tickets = [t for t in tickets if query in " ".join([
            t["type"], t["status"], t["assignee"], t["sprint"],
            " ".join(t["labels"]), t["title"]
        ]).lower()]

    if not tickets:
        continue

    type_count = Counter(t["type"] for t in tickets)
    status_count = Counter(t["status"] for t in tickets)
    priority_count = Counter(t["priority"] for t in tickets)
    assignee_count = Counter(t["assignee"] for t in tickets)

    print(f"=== {month} — {len(tickets)} tickets ===")
    print(f"Par type     : {dict(type_count)}")
    print(f"Par statut   : {dict(status_count)}")
    print(f"Par priorité : {dict(priority_count)}")
    print(f"Par assignee : {dict(assignee_count)}")

    bugs = [t for t in tickets if t["type"] == "bug"]
    features = [t for t in tickets if t["type"] == "feature"]
    ratio = f"{len(bugs)}/{len(features)}" if features else f"{len(bugs)}/0"
    print(f"Ratio bug/feature : {ratio}")
    print()
