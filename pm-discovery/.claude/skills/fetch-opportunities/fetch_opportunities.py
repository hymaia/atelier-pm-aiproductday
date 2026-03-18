from __future__ import annotations
import sys
from pathlib import Path

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.interview_loader import load

data_dir = project_dir / "data" / "interviews"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

interviews = []
for f in sorted(data_dir.glob("*.md")):
    interview = load(f)
    if not query:
        interviews.append(interview)
    else:
        searchable = " ".join([
            interview["persona"],
            interview["client"],
            " ".join(interview["themes"]),
            interview["content"],
        ]).lower()
        if query in searchable:
            interviews.append(interview)

if not interviews:
    print(f"AUCUNE DONNÉE — aucune interview trouvée pour : '{query}'")
    sys.exit(0)

print(f"FILTRE : {query or 'toutes les interviews'}")
print(f"INTERVIEWS ANALYSÉES : {len(interviews)}\n")

for iv in interviews:
    client_label = iv["client"] if iv["client"] else "Persona anonymisé"
    print(f"=== {iv['date']} : {iv['persona']} ({client_label}) ===")
    print(f"Thèmes : {', '.join(iv['themes'])}")
    print(iv['content'])
    print()
