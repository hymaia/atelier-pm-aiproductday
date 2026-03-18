from __future__ import annotations
import sys
from pathlib import Path

skill_dir = Path(__file__).parent
project_dir = skill_dir.parents[2]
sys.path.insert(0, str(project_dir))

from utils.code_loader import load

data_dir = project_dir / "data" / "source"
query = " ".join(sys.argv[1:]).lower().strip() if len(sys.argv) > 1 else ""

files = []
for f in sorted(data_dir.glob("*")):
    if f.suffix.lower() in {".py", ".ts", ".js", ".go", ".java", ".rs", ".rb", ".php"}:
        files.append(f)

if not files:
    print("AUCUNE DONNÉE — aucun fichier source trouvé dans data/source/")
    sys.exit(0)

# Filtrage par query si fournie
if query:
    matched = [f for f in files if query in f.name.lower()]
    # Si pas de match exact sur le nom, chercher dans le contenu
    if not matched:
        matched = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8").lower()
                if query in content:
                    matched.append(f)
            except Exception:
                pass
    files = matched if matched else files  # fallback : tout charger

if not files:
    print(f"AUCUNE DONNÉE — aucun fichier correspondant à : '{query}'")
    sys.exit(0)

print(f"REQUÊTE : {query or 'tous les fichiers source'}")
print(f"FICHIERS TROUVÉS : {len(files)}\n")

for f in files:
    code = load(f)
    print(f"=== {code['filename']} ({code['language']}) ===")
    print(code["content"])
    print()
