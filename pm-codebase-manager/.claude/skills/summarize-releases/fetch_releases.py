from __future__ import annotations
import sys
from pathlib import Path

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.release_loader import load

data_dir = project_dir / "data" / "releases"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

releases = []
for f in sorted(data_dir.glob("*.md"), reverse=True):  # plus récent en premier
    releases.append(load(f))

if not releases:
    print("AUCUNE DONNÉE — aucun changelog trouvé dans data/releases/")
    sys.exit(0)

# Filtrage par query si fournie (version, date, client mentionné dans le contenu)
if query:
    matched = [r for r in releases if query in r["content"].lower() or query in r["version"].lower()]
    releases = matched if matched else releases  # fallback : tout retourner

if not releases:
    print(f"AUCUNE DONNÉE — aucun changelog correspondant à : '{query}'")
    sys.exit(0)

print(f"REQUÊTE : {query or 'tous les changelogs'}")
print(f"RELEASES TROUVÉES : {len(releases)}\n")

for r in releases:
    print(f"=== v{r['version']} — {r['date']} ({r['filename']}) ===")
    print(r["content"])
    print()
