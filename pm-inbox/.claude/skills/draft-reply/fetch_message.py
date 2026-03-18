from __future__ import annotations
import sys
from pathlib import Path

# Racine du module pm-inbox (4 niveaux au-dessus du script)
project_dir = Path(__file__).parents[3]
sys.path.insert(0, str(project_dir))

from utils.email_loader import load as load_email
from utils.slack_loader import load as load_slack

query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

if not query:
    print("ERREUR : précise un nom d'expéditeur ou un mot-clé du sujet.")
    sys.exit(1)

data_dir = project_dir / "data"
all_messages = []

for f in sorted((data_dir / "emails").glob("*.md")):
    all_messages.extend(load_email(f))

for f in sorted((data_dir / "slack").glob("*.md")):
    all_messages.extend(load_slack(f))

matches = [
    msg for msg in all_messages
    if query in msg["from"].lower()
    or query in msg["subject"].lower()
    or query in msg["body"].lower()
    or query in (msg["channel"] or "").lower()
]

if not matches:
    print(f"AUCUN MESSAGE trouvé pour la recherche : '{query}'")
    sys.exit(0)

for msg in matches:
    source = f"[{msg['type'].upper()}]"
    print(f"=== {source} {msg['subject']} ===")
    print(f"De     : {msg['from']}")
    print(f"Date   : {msg['date']}")
    if msg["channel"]:
        print(f"Canal  : #{msg['channel']}")
    print(f"\n{msg['body']}\n")
