from __future__ import annotations
import sys
from pathlib import Path

# Racine du module pm-inbox (4 niveaux au-dessus du script)
project_dir = Path(__file__).parents[3]
sys.path.insert(0, str(project_dir))

from utils.email_loader import load as load_email
from utils.slack_loader import load as load_slack

data_dir = project_dir / "data"
messages = []

for f in sorted((data_dir / "emails").glob("*.md")):
    messages.extend(load_email(f))

for f in sorted((data_dir / "slack").glob("*.md")):
    messages.extend(load_slack(f))

if not messages:
    print("AUCUN MESSAGE EN ATTENTE")
    sys.exit(0)

print(f"MESSAGES EN ATTENTE : {len(messages)}\n")

for msg in messages:
    source = f"[{msg['type'].upper()}]"
    print(f"=== {source} {msg['subject']} ===")
    print(f"De     : {msg['from']}")
    print(f"Date   : {msg['date']}")
    if msg["channel"]:
        print(f"Canal  : #{msg['channel']}")
    print(f"Fichier: {msg['filename']}")
    print(f"\n{msg['body']}\n")
