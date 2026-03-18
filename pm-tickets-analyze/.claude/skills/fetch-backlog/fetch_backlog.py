from __future__ import annotations
import sys
from pathlib import Path

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.ticket_loader import load

MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}

data_dir = project_dir / "data" / "tickets"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

# Charger tous les tickets (fichiers les plus récents en premier)
all_tickets = []
for f in sorted(data_dir.glob("*.csv"), reverse=True):
    all_tickets.extend(load(f))

if not all_tickets:
    print("AUCUNE DONNÉE — aucun fichier de tickets trouvé.")
    sys.exit(0)

# Convertir mois français
search_query = query
for mois, num in MOIS_FR.items():
    if mois in query:
        search_query = query.replace(mois, f"-{num}-")

# Filtrer selon la requête
def matches(ticket: dict) -> bool:
    if not query:
        return ticket["status"] != "done"  # Par défaut : tickets non terminés
    searchable = " ".join([
        ticket["id"], ticket["title"], ticket["type"], ticket["status"],
        ticket["priority"], ticket["assignee"], ticket["sprint"],
        ticket["created_at"], " ".join(ticket["labels"]),
    ]).lower()
    return search_query in searchable or query in searchable

tickets = [t for t in all_tickets if matches(t)]

if not tickets:
    print(f"AUCUNE DONNÉE — aucun ticket trouvé pour : '{query}'")
    sys.exit(0)

# Grouper par statut pour la lisibilité
STATUS_ORDER = ["blocked", "in_progress", "in_review", "todo", "done"]
tickets.sort(key=lambda t: (STATUS_ORDER.index(t["status"]) if t["status"] in STATUS_ORDER else 99, t["priority"]))

print(f"FILTRE : {query or 'tickets actifs (hors done)'}")
print(f"TICKETS TROUVÉS : {len(tickets)}\n")

current_status = None
for t in tickets:
    if t["status"] != current_status:
        current_status = t["status"]
        print(f"── {current_status.upper()} ──")
    labels = f" [{', '.join(t['labels'])}]" if t["labels"] else ""
    print(f"  {t['id']} | {t['priority'].upper():8} | {t['assignee']:15} | {t['title']}{labels}")
print()
