from pathlib import Path

skill_dir = Path(__file__).parent
data_dir = skill_dir.parents[2] / "data"

files = sorted(data_dir.rglob("*.md"))
for f in files:
    print(f.name)
